# 🎵 Pi Pitch Pal

A YouTube audio extractor built with SvelteKit. Download YouTube videos, extract audio as MP3, and manage your audio library.

## Features

- 🎬 Extract audio from YouTube videos
- 🎧 Built-in audio player
- 📁 Audio library management
- ⬇️ Download extracted audio files
- 🗑️ Delete unwanted files

## Prerequisites

### yt-dlp

This app requires `yt-dlp` to be installed on your system.

**macOS:**

```bash
brew install yt-dlp
```

**Linux (Ubuntu/Debian):**

```bash
sudo add-apt-repository ppa:tomtomtom/yt-dlp
sudo apt update
sudo apt install yt-dlp
```

**Linux (other):**

```bash
pip install yt-dlp
```

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd pi_pitch_pal

# Install dependencies
pnpm install
```

## Development

```bash
pnpm dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Usage

1. Paste a YouTube URL into the input field
2. Click "Extract Audio"
3. Wait for the download to complete
4. Play, download, or delete audio files from the library

## Tech Stack

- [SvelteKit](https://kit.svelte.dev/) - Full-stack framework
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
