import { mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

const AUDIO_DIR = 'static/audio';

// Ensure audio directory exists
export async function ensureAudioDir() {
	if (!existsSync(AUDIO_DIR)) {
		await mkdir(AUDIO_DIR, { recursive: true });
	}
}

export interface DownloadResult {
	success: boolean;
	filename?: string;
	title?: string;
	error?: string;
}

export async function downloadAudio(youtubeUrl: string): Promise<DownloadResult> {
	await ensureAudioDir();

	try {
		console.log('🎬 [Download] Starting download for:', youtubeUrl);

		// Use yt-dlp output template - single call, no separate info fetch
		const outputTemplate = path.join(AUDIO_DIR, '%(title).50s_%(id)s.%(ext)s');

		console.log('⬇️  [Download] Downloading and extracting audio...');

		// Use spawn to run yt-dlp directly - more reliable than the wrapper
		const { spawn } = await import('child_process');

		const result = await new Promise<{ filename: string; title: string }>((resolve, reject) => {
			const args = [
				youtubeUrl,
				'-x',
				'--audio-format', 'mp3',
				'--audio-quality', '256K',
				'-o', outputTemplate,
				'--no-playlist',
				'--print', 'after_move:filepath', // Print the final filename
				'--restrict-filenames' // Safe filenames
			];

			console.log('📋 [Download] Running: yt-dlp', args.join(' '));

			const proc = spawn('yt-dlp', args);
			let output = '';
			let errorOutput = '';

			proc.stdout.on('data', (data) => {
				const line = data.toString();
				output += line;
				console.log('📥 [yt-dlp]', line.trim());
			});

			proc.stderr.on('data', (data) => {
				const line = data.toString();
				errorOutput += line;
				console.log('⚠️  [yt-dlp]', line.trim());
			});

			proc.on('close', (code) => {
				if (code === 0) {
					const filepath = output.trim().split('\n').pop() || '';
					const filename = path.basename(filepath);
					const title = filename.replace(/_[^_]+\.mp3$/, '').replace(/_/g, ' ');
					resolve({ filename, title });
				} else {
					reject(new Error(errorOutput || `yt-dlp exited with code ${code}`));
				}
			});

			proc.on('error', (err) => {
				reject(err);
			});
		});

		console.log('✅ [Download] Complete:', result.filename);

		return {
			success: true,
			filename: result.filename,
			title: result.title
		};
	} catch (error) {
		console.error('❌ [Download] Error:', error);
		return {
			success: false,
			error: error instanceof Error ? error.message : 'Failed to download audio'
		};
	}
}

export interface AudioFile {
	filename: string;
	title: string;
	url: string;
}

export async function getAudioFiles(): Promise<AudioFile[]> {
	await ensureAudioDir();

	const { readdir } = await import('fs/promises');
	const files = await readdir(AUDIO_DIR);

	return files
		.filter((file) => file.endsWith('.mp3'))
		.map((filename) => ({
			filename,
			title: filename.replace(/_[^_]+\.mp3$/, '').replace(/_/g, ' '),
			url: `/audio/${filename}`
		}));
}

export async function deleteAudioFile(filename: string): Promise<boolean> {
	const { unlink } = await import('fs/promises');
	const filepath = path.join(AUDIO_DIR, filename);

	try {
		if (existsSync(filepath)) {
			await unlink(filepath);
			return true;
		}
		return false;
	} catch {
		return false;
	}
}
