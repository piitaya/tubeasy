# Tubeasy

Petite interface self-hosted pour télécharger une vidéo YouTube en MP3 ou MP4 depuis un simple lien. Construite avec [yt-dlp](https://github.com/yt-dlp/yt-dlp), FastAPI et un poil de vanilla JS.

[![Docker](https://github.com/piitaya/tubeasy/actions/workflows/docker.yml/badge.svg)](https://github.com/piitaya/tubeasy/actions/workflows/docker.yml)

## Démarrage rapide (image pré-buildée)

L'image est publiée sur GitHub Container Registry à chaque push sur `main` (multi-arch `amd64` + `arm64`, donc OK sur Raspberry Pi, NAS, etc.).

`docker-compose.yml` :

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

Puis :

```bash
docker compose up -d
```

Ouvre [http://localhost:8000](http://localhost:8000). Les fichiers atterrissent dans `./downloads/`.

## Utilisation

1. Colle l'URL de la vidéo YouTube
2. Choisis MP3 ou MP4
3. Clique "Télécharger"
4. Récupère le fichier depuis l'historique (lien direct ou suppression)

## Build local

Si tu préfères builder l'image toi-même (depuis une copie du repo) :

```bash
docker compose up -d --build
```

## Mise à jour

Image pré-buildée :

```bash
docker compose pull && docker compose up -d
```

Build local :

```bash
docker compose build --no-cache && docker compose up -d
```

## Cookies (optionnel)

Si YouTube te demande de prouver que tu n'es pas un robot, exporte un fichier `cookies.txt` (extension Chrome "Get cookies.txt LOCALLY" par exemple), pose-le à la racine du projet, ajoute le mount dans `docker-compose.yml` :

```yaml
    volumes:
      - ./downloads:/app/downloads
      - ./cookies.txt:/app/cookies.txt:ro
```

Puis passe `cookiefile: "/app/cookies.txt"` dans les options yt-dlp côté `app/main.py`.

## Tags d'image disponibles

- `latest` — dernier build de `main`
- `vX.Y.Z` — release taguée (push d'un tag git `v*.*.*`)
- `X.Y` — alias majeur.mineur
- `main` — alias de la branche
- `pr-N` / `sha-XXXXXXX` — builds intermédiaires

## Structure

```
.
├── app/
│   ├── main.py        # FastAPI
│   └── static/
│       └── index.html # UI
├── .github/workflows/
│   └── docker.yml     # build + push GHCR
├── downloads/         # fichiers téléchargés (créé au runtime)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Licence

MIT
