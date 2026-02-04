<script lang="ts">
	import { PitchShifter } from 'soundtouchjs';
	import { onMount } from 'svelte';

	interface Props {
		src: string;
		title: string;
	}

	let { src, title }: Props = $props();

	let audioContext: AudioContext | null = $state(null);
	let shifter: PitchShifter | null = $state(null);
	let gainNode: GainNode | null = $state(null);
	let audioBuffer: AudioBuffer | null = $state(null);

	let isPlaying = $state(false);
	let isLoading = $state(true);
	let loadError = $state(false);
	let pitch = $state(0); // semitones (-12 to +12)
	let volume = $state(100); // percentage
	let progress = $state(0); // current time in seconds
	let duration = $state(0);
	let startTime = $state(0); // when playback started (AudioContext time)
	let startOffset = $state(0); // offset from seeking
	let animationFrameId: number | null = null;

	// Convert semitones to pitch multiplier
	const pitchMultiplier = $derived(Math.pow(2, pitch / 12));

	// Progress as percentage for the slider
	const progressPercent = $derived(duration > 0 ? (progress / duration) * 100 : 0);

	// Pitch labels for display
	const pitchLabel = $derived(() => {
		if (pitch === 0) return 'Original';
		const sign = pitch > 0 ? '+' : '';
		return `${sign}${pitch} semitones`;
	});

	onMount(() => {
		loadAudio();

		return () => {
			cleanup();
		};
	});

	function cleanup() {
		if (animationFrameId) {
			cancelAnimationFrame(animationFrameId);
			animationFrameId = null;
		}
		if (shifter) {
			try {
				shifter.off();
				shifter.disconnect();
			} catch (e) {
				// Ignore cleanup errors
			}
			shifter = null;
		}
		if (audioContext && audioContext.state !== 'closed') {
			audioContext.close();
		}
	}

	async function loadAudio() {
		try {
			audioContext = new AudioContext();
			gainNode = audioContext.createGain();
			gainNode.connect(audioContext.destination);

			const response = await fetch(src);
			if (!response.ok) {
				throw new Error('Failed to fetch audio');
			}
			const arrayBuffer = await response.arrayBuffer();
			audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
			duration = audioBuffer.duration;
			console.log('Audio loaded, duration:', duration);
			isLoading = false;
		} catch (err) {
			console.error('Error loading audio:', err);
			isLoading = false;
			loadError = true;
		}
	}

	function updateProgress() {
		if (audioContext && isPlaying) {
			// Calculate progress based on AudioContext time
			const elapsed = audioContext.currentTime - startTime;
			progress = startOffset + elapsed;

			if (progress >= duration) {
				// Playback finished
				stopPlayback();
				progress = 0;
				startOffset = 0;
			} else {
				animationFrameId = requestAnimationFrame(updateProgress);
			}
		}
	}

	function createShifter(fromPosition: number = 0) {
		if (!audioContext || !audioBuffer || !gainNode) return;

		shifter = new PitchShifter(audioContext, audioBuffer, 16384);
		shifter.pitch = pitchMultiplier;

		// Set starting position if not from beginning
		if (fromPosition > 0 && duration > 0) {
			shifter.percentagePlayed = fromPosition / duration;
		}

		shifter.connect(gainNode);
	}

	function stopPlayback() {
		if (animationFrameId) {
			cancelAnimationFrame(animationFrameId);
			animationFrameId = null;
		}
		// Save current position for resume
		if (audioContext && isPlaying) {
			startOffset = progress;
		}
		if (shifter) {
			try {
				shifter.off();
				shifter.disconnect();
			} catch (e) {
				// Ignore
			}
			shifter = null;
		}
		isPlaying = false;
	}

	async function togglePlay() {
		if (!audioContext || !audioBuffer || !gainNode) return;

		// Resume audio context if suspended (browser autoplay policy)
		if (audioContext.state === 'suspended') {
			await audioContext.resume();
		}

		if (isPlaying) {
			stopPlayback();
		} else {
			createShifter(startOffset);
			startTime = audioContext.currentTime;
			isPlaying = true;
			// Start progress tracking
			animationFrameId = requestAnimationFrame(updateProgress);
		}
	}

	function handlePitchChange(e: Event) {
		const target = e.target as HTMLInputElement;
		pitch = parseInt(target.value);
		if (shifter) {
			shifter.pitch = pitchMultiplier;
		}
	}

	function handleVolumeChange(e: Event) {
		const target = e.target as HTMLInputElement;
		volume = parseInt(target.value);
		if (gainNode) {
			gainNode.gain.value = volume / 100;
		}
	}

	function handleSeek(e: Event) {
		if (!audioContext) return;

		const target = e.target as HTMLInputElement;
		const newPercent = parseFloat(target.value);
		const newPosition = (newPercent / 100) * duration;

		progress = newPosition;
		startOffset = newPosition;

		if (isPlaying && shifter) {
			// Restart playback from new position
			stopPlayback();
			createShifter(newPosition);
			startTime = audioContext.currentTime;
			isPlaying = true;
			animationFrameId = requestAnimationFrame(updateProgress);
		}
	}

	function formatTime(seconds: number): string {
		if (seconds === null || seconds === undefined || !isFinite(seconds) || isNaN(seconds)) {
			return '0:00';
		}
		const mins = Math.floor(seconds / 60);
		const secs = Math.floor(seconds % 60);
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}
</script>

<div class="rounded-xl bg-white/5 p-4">
	<h3 class="mb-3 truncate font-medium text-white" {title}>
		{title}
	</h3>

	{#if isLoading}
		<div class="flex items-center justify-center py-4">
			<div
				class="h-6 w-6 animate-spin rounded-full border-2 border-purple-400 border-t-transparent"
			></div>
			<span class="ml-2 text-purple-300">Loading...</span>
		</div>
	{:else if loadError}
		<div class="py-4 text-center text-red-400">Failed to load audio</div>
	{:else}
		<!-- Play/Pause and Progress -->
		<div class="mb-4 flex items-center gap-4">
			<button
				onclick={togglePlay}
				class="flex h-12 w-12 flex-shrink-0 cursor-pointer items-center justify-center rounded-full bg-purple-600 text-white transition hover:bg-purple-500"
			>
				{#if isPlaying}
					<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
						<rect x="6" y="4" width="4" height="16" />
						<rect x="14" y="4" width="4" height="16" />
					</svg>
				{:else}
					<svg class="ml-1 h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
						<path d="M8 5v14l11-7z" />
					</svg>
				{/if}
			</button>

			<div class="flex-1">
				<div class="text-sm text-purple-300">
					{formatTime(progress)} / {formatTime(duration)}
				</div>
				<input
					type="range"
					min="0"
					max="100"
					step="0.1"
					value={progressPercent}
					oninput={handleSeek}
					class="mt-1 h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/20 accent-purple-500"
				/>
			</div>
		</div>

		<!-- Pitch Control -->
		<div class="mb-3">
			<div class="mb-1 flex items-center justify-between">
				<label class="text-sm font-medium text-purple-200">Pitch</label>
				<span class="text-sm text-purple-400">{pitchLabel()}</span>
			</div>
			<input
				type="range"
				min="-12"
				max="12"
				step="1"
				value={pitch}
				oninput={handlePitchChange}
				class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/20 accent-purple-500"
			/>
			<div class="mt-1 flex justify-between text-xs text-purple-400/70">
				<span>-12</span>
				<span>0</span>
				<span>+12</span>
			</div>
		</div>

		<!-- Volume Control -->
		<div>
			<div class="mb-1 flex items-center justify-between">
				<label class="text-sm font-medium text-purple-200">Volume</label>
				<span class="text-sm text-purple-400">{volume}%</span>
			</div>
			<input
				type="range"
				min="0"
				max="100"
				step="1"
				value={volume}
				oninput={handleVolumeChange}
				class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/20 accent-purple-500"
			/>
		</div>
	{/if}
</div>
