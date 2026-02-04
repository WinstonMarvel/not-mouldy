<script lang="ts">
	import { enhance } from '$app/forms';
	import type { ActionData, PageData } from './$types';
	import AudioPlayer from '$lib/components/AudioPlayer.svelte';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let isLoading = $state(false);
	let videoUrl = $state('');

	// Track which file is being renamed
	let renamingFile = $state<string | null>(null);
	let newTitle = $state('');

	// Reactive audio files from server data
	let audioFiles = $derived(data.audioFiles);

	function startRename(filename: string, currentTitle: string) {
		renamingFile = filename;
		newTitle = currentTitle;
	}

	function cancelRename() {
		renamingFile = null;
		newTitle = '';
	}
</script>

<svelte:head>
	<title>Pi Pitch Pal - Audio Extractor</title>
</svelte:head>

<main class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
	<div class="container mx-auto px-4 py-12">
		<!-- Header -->
		<header class="mb-12 text-center">
			<h1 class="mb-2 text-4xl font-bold text-white">🎵 Pi Pitch Pal</h1>
			<p class="text-lg text-purple-300">Extract audio from any video</p>
		</header>

		<!-- Download Form -->
		<section class="mx-auto mb-12 max-w-2xl">
			<div class="rounded-2xl bg-white/10 p-8 shadow-2xl backdrop-blur-lg">
				<h2 class="mb-6 text-xl font-semibold text-white">Download Audio</h2>

				<form
					method="POST"
					action="?/download"
					use:enhance={() => {
						isLoading = true;
						return async ({ update }) => {
							await update();
							isLoading = false;
							videoUrl = '';
						};
					}}
					class="space-y-4"
				>
					<div>
						<label for="url" class="mb-2 block text-sm font-medium text-purple-200">
							Video URL
						</label>
						<input
							type="url"
							id="url"
							name="url"
							bind:value={videoUrl}
							placeholder="Paste video link here..."
							required
							disabled={isLoading}
							class="w-full rounded-lg border border-purple-500/30 bg-white/5 px-4 py-3 text-white placeholder-purple-300/50 transition focus:border-purple-400 focus:ring-2 focus:ring-purple-400/50 focus:outline-none disabled:opacity-50"
						/>
					</div>

					<button
						type="submit"
						disabled={isLoading || !videoUrl}
						class="w-full cursor-pointer rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 font-semibold text-white transition hover:from-purple-500 hover:to-pink-500 disabled:cursor-not-allowed disabled:opacity-50"
					>
						{#if isLoading}
							<span class="flex items-center justify-center gap-2">
								<svg class="h-5 w-5 animate-spin" viewBox="0 0 24 24">
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
										fill="none"
									></circle>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
									></path>
								</svg>
								Downloading...
							</span>
						{:else}
							🎬 Extract Audio
						{/if}
					</button>
				</form>

				<!-- Status Messages -->
				{#if form?.error}
					<div class="mt-4 rounded-lg bg-red-500/20 p-4 text-red-200">
						❌ {form.error}
					</div>
				{/if}

				{#if form?.success}
					<div class="mt-4 rounded-lg bg-green-500/20 p-4 text-green-200">
						✅ {form.message}
					</div>
				{/if}
			</div>
		</section>

		<!-- Audio Library -->
		<section class="mx-auto max-w-4xl">
			<div class="rounded-2xl bg-white/10 p-8 shadow-2xl backdrop-blur-lg">
				<h2 class="mb-6 text-xl font-semibold text-white">🎧 Audio Library</h2>

				{#if audioFiles.length === 0}
					<div class="py-12 text-center text-purple-300/70">
						<p class="text-lg">No audio files yet</p>
						<p class="text-sm">Download your first audio above!</p>
					</div>
				{:else}
					<div class="grid gap-6 md:grid-cols-2">
						{#each audioFiles as audio (audio.filename)}
							<div class="relative">
								<AudioPlayer src={audio.url} title={audio.title} />

								<!-- Rename Form (shown when editing) -->
								{#if renamingFile === audio.filename}
									<form
										method="POST"
										action="?/rename"
										class="mt-3"
										use:enhance={() => {
											return async ({ update }) => {
												await update();
												cancelRename();
											};
										}}
									>
										<input type="hidden" name="filename" value={audio.filename} />
										<div class="flex gap-2">
											<input
												type="text"
												name="newTitle"
												bind:value={newTitle}
												placeholder="Enter new title"
												required
												class="flex-1 rounded-lg border border-purple-500/30 bg-white/5 px-3 py-2 text-sm text-white placeholder-purple-300/50 focus:border-purple-400 focus:ring-1 focus:ring-purple-400/50 focus:outline-none"
											/>
											<button
												type="submit"
												class="cursor-pointer rounded-lg bg-green-600/50 px-3 py-2 text-sm font-medium text-white transition hover:bg-green-600"
											>
												✓
											</button>
											<button
												type="button"
												onclick={cancelRename}
												class="cursor-pointer rounded-lg bg-gray-600/50 px-3 py-2 text-sm font-medium text-white transition hover:bg-gray-600"
											>
												✕
											</button>
										</div>
									</form>
								{:else}
									<!-- Actions -->
									<div class="mt-3 flex gap-2">
										<button
											onclick={() => startRename(audio.filename, audio.title)}
											class="flex-1 cursor-pointer rounded-lg bg-blue-600/50 px-4 py-2 text-center text-sm font-medium text-white transition hover:bg-blue-600"
										>
											✏️ Rename
										</button>

										<a
											href={audio.url}
											download={audio.filename}
											class="flex-1 rounded-lg bg-purple-600/50 px-4 py-2 text-center text-sm font-medium text-white transition hover:bg-purple-600"
										>
											⬇️ Download
										</a>

										<form
											method="POST"
											action="?/delete"
											class="flex-1"
											use:enhance={() => {
												return async ({ update }) => {
													await update();
												};
											}}
										>
											<input type="hidden" name="filename" value={audio.filename} />
											<button
												type="submit"
												class="w-full cursor-pointer rounded-lg bg-red-600/50 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-600"
												onclick={(e) => {
													if (!confirm('Are you sure you want to delete this audio file?')) {
														e.preventDefault();
													}
												}}
											>
												🗑️ Delete
											</button>
										</form>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</section>
	</div>
</main>
