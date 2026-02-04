import type { Actions, PageServerLoad } from './$types';
import { downloadAudio, getAudioFiles, deleteAudioFile } from '$lib/server/audio';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async () => {
	const audioFiles = await getAudioFiles();
	return { audioFiles };
};

export const actions: Actions = {
	download: async ({ request }) => {
		const formData = await request.formData();
		const url = formData.get('url')?.toString();

		if (!url) {
			return fail(400, { error: 'Please provide a video URL' });
		}

		// Basic URL validation - yt-dlp supports 1000+ sites
		const urlRegex = /^https?:\/\/.+/;
		if (!urlRegex.test(url)) {
			return fail(400, { error: 'Please provide a valid URL' });
		}

		const result = await downloadAudio(url);

		if (!result.success) {
			return fail(500, { error: result.error || 'Failed to download audio' });
		}

		return {
			success: true,
			message: `Successfully downloaded: ${result.title}`,
			filename: result.filename
		};
	},

	delete: async ({ request }) => {
		const formData = await request.formData();
		const filename = formData.get('filename')?.toString();

		if (!filename) {
			return fail(400, { error: 'No filename provided' });
		}

		const deleted = await deleteAudioFile(filename);

		if (!deleted) {
			return fail(500, { error: 'Failed to delete file' });
		}

		return { success: true, message: 'File deleted successfully' };
	}
};
