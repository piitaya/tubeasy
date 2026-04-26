from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOWNLOADS_DIR = Path(os.environ.get("DOWNLOADS_DIR", BASE_DIR.parent / "downloads"))
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Tubeasy")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class DownloadRequest(BaseModel):
    url: HttpUrl
    format: Literal["mp3", "mp4"]


def _ydl_opts(fmt: str) -> dict:
    outtmpl = str(DOWNLOADS_DIR / "%(title)s.%(ext)s")
    common = {
        "outtmpl": outtmpl,
        "noplaylist": True,
        "restrictfilenames": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }
    if fmt == "mp3":
        return {
            **common,
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
    return {
        **common,
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
    }


def _resolve_safe(filename: str) -> Path:
    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    target = (DOWNLOADS_DIR / filename).resolve()
    try:
        target.relative_to(DOWNLOADS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return target


def _file_meta(path: Path) -> dict:
    stat = path.stat()
    return {
        "filename": path.name,
        "size": stat.st_size,
        "mtime": stat.st_mtime,
    }


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))


@app.get("/api/files")
def list_files() -> list[dict]:
    files = [p for p in DOWNLOADS_DIR.iterdir() if p.is_file() and not p.name.startswith(".")]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [_file_meta(p) for p in files]


@app.get("/api/files/{filename}")
def get_file(filename: str) -> FileResponse:
    target = _resolve_safe(filename)
    return FileResponse(target, filename=target.name, media_type="application/octet-stream")


@app.delete("/api/files/{filename}")
def delete_file(filename: str) -> dict:
    target = _resolve_safe(filename)
    target.unlink()
    return {"ok": True}


@app.post("/api/download")
def download(req: DownloadRequest) -> dict:
    opts = _ydl_opts(req.format)
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(str(req.url), download=True)
    except DownloadError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    if info is None:
        raise HTTPException(status_code=400, detail="No video info returned")

    if "entries" in info and info["entries"]:
        info = info["entries"][0]

    filepath = Path(info.get("requested_downloads", [{}])[0].get("filepath") or "")
    if not filepath or not filepath.exists():
        # Fallback: rebuild expected path
        with YoutubeDL(opts) as ydl:
            base = ydl.prepare_filename(info)
        candidate = Path(base)
        if req.format == "mp3":
            candidate = candidate.with_suffix(".mp3")
        if not candidate.exists():
            raise HTTPException(status_code=500, detail="Downloaded file not found")
        filepath = candidate

    return _file_meta(filepath)
