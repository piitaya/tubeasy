# Tubeasy

Self-hosted web UI to download YouTube videos as MP3 or MP4. Paste a link, click, get the file. Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp), FastAPI, and a sprinkle of vanilla JS.

[![Docker](https://github.com/piitaya/tubeasy/actions/workflows/docker.yml/badge.svg)](https://github.com/piitaya/tubeasy/actions/workflows/docker.yml)

## Quick start (prebuilt image)

The image is published to GitHub Container Registry on every push to `main` (multi-arch `amd64` + `arm64`, so it runs fine on Raspberry Pi, NAS, etc.).

`docker-compose.yml`:

```yaml
services:
  tubeasy:
    image: ghcr.io/piitaya/tubeasy:latest
    container_name: tubeasy
    ports:
      - "8000:8000"
    volumes:
      - ./downloads:/app/downloads
    restart: unless-stopped
```

Then:

```bash
docker compose up -d
```

Open [http://localhost:8000](http://localhost:8000). Files land in `./downloads/`.

## Usage

1. Paste the YouTube URL
2. Pick MP3 or MP4
3. Click "Download"
4. Grab the file from the history (direct link or delete)

## Build locally

If you'd rather build the image yourself (from a clone of the repo):

```bash
docker compose up -d --build
```

## Updating

Prebuilt image:

```bash
docker compose pull && docker compose up -d
```

Local build:

```bash
docker compose build --no-cache && docker compose up -d
```

## Cookies (optional)

If YouTube asks you to prove you're not a bot, export a `cookies.txt` file (e.g. with the "Get cookies.txt LOCALLY" Chrome extension), drop it at the project root, then add the mount in `docker-compose.yml`:

```yaml
    volumes:
      - ./downloads:/app/downloads
      - ./cookies.txt:/app/cookies.txt:ro
```

Then pass `cookiefile: "/app/cookies.txt"` in the yt-dlp options in `app/main.py`.

## Available image tags

- `latest` — latest build from `main`
- `vX.Y.Z` — tagged release (push a `v*.*.*` git tag)
- `X.Y` — major.minor alias
- `main` — branch alias
- `pr-N` / `sha-XXXXXXX` — intermediate builds

## Structure

```
.
├── app/
│   ├── main.py        # FastAPI
│   └── static/
│       └── index.html # UI
├── .github/workflows/
│   └── docker.yml     # build + push to GHCR
├── downloads/         # downloaded files (created at runtime)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Credits

Built with [Claude](https://claude.ai/) on a day I'd had enough of overcomplicated YouTube downloader projects.

## License

MIT
