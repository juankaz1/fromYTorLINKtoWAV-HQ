# /// script
# requires-python = ">=3.9"
# dependencies = ["yt-dlp>=2025.1.0"]
# ///

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


def ffmpeg_executable() -> str:
    local = Path(__file__).resolve().parent / ".tools" / "ffmpeg.exe"
    return str(local) if local.is_file() else "ffmpeg"


def ffmpeg_options() -> dict:
    local = Path(__file__).resolve().parent / ".tools" / "ffmpeg.exe"
    return {"ffmpeg_location": str(local)} if local.is_file() else {}


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Introduce una URL HTTP o HTTPS valida.")

    host = parsed.hostname.lower()
    if host in ("spotify.com", "open.spotify.com", "tidal.com", "listen.tidal.com") or host.endswith((".spotify.com", ".tidal.com")):
        raise ValueError("Spotify y Tidal no ofrecen el audio de sus canciones mediante un enlace publico. No se admite extraer contenido protegido por DRM.")


def available_video_qualities(url: str) -> list[int]:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError

    validate_url(url)
    try:
        with YoutubeDL({"skip_download": True, "noplaylist": True, "quiet": True, "no_warnings": True,
                **ffmpeg_options()}) as downloader:
            info = downloader.extract_info(url, download=False)
    except DownloadError as exc:
        raise ValueError(f"No se pudieron consultar las calidades: {exc}") from exc
    if not info or "entries" in info:
        raise ValueError("El enlace no corresponde a un video individual.")
    return sorted({height for video_format in info.get("formats", [])
                   if video_format.get("vcodec") not in (None, "none")
                   for height in [video_format.get("height")]
                   if isinstance(height, int) and height > 0}, reverse=True)


def download_video(url: str, output_dir: Path, height: Optional[int] = None) -> Path:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError

    validate_url(url)
    if not output_dir.is_dir():
        raise ValueError(f"La carpeta de destino no existe: {output_dir}")
    if height is not None and (not isinstance(height, int) or height <= 0):
        raise ValueError("Elige una resolucion de video valida.")

    video_format = f"bv[height={height}]+ba/b[height={height}]" if height else "bv+ba/b"
    with tempfile.TemporaryDirectory() as temp_dir:
        options = {
            "format": video_format,
            "merge_output_format": "mkv",
            **ffmpeg_options(),
            "noplaylist": True,
            "outtmpl": str(Path(temp_dir) / "%(title).180B [%(id)s].%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
        except DownloadError as exc:
            raise ValueError(f"No se pudo descargar el video: {exc}") from exc
        if not info or "entries" in info:
            raise ValueError("El enlace no corresponde a un video individual descargable.")

        source = Path(info.get("filepath") or "")
        if not source.is_file():
            files = [path for path in Path(temp_dir).iterdir() if path.is_file()]
            if len(files) != 1:
                raise ValueError("No se encontro el archivo de video descargado.")
            source = files[0]

        target = output_dir / source.name
        if target.exists():
            raise ValueError(f"El archivo ya existe y no se sobrescribira: {target}")
        shutil.move(str(source), str(target))
        return target


def download_wav(url: str, output_dir: Path) -> Path:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError

    validate_url(url)
    if not output_dir.is_dir():
        raise ValueError(f"La carpeta de destino no existe: {output_dir}")

    with tempfile.TemporaryDirectory() as temp_dir:
        options = {
            "format": "bestaudio/best",
            **ffmpeg_options(),
            "noplaylist": True,
            "outtmpl": str(Path(temp_dir) / "%(title).180B [%(id)s].%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
        except DownloadError as exc:
            raise ValueError(f"No se pudo descargar el audio de ese enlace: {exc}") from exc

        if not info or "entries" in info:
            raise ValueError("El enlace no corresponde a una pista individual descargable.")
        downloads = info.get("requested_downloads") or []
        if not downloads or not downloads[0].get("filepath"):
            raise ValueError("No se encontro el archivo de audio descargado.")

        source = Path(downloads[0]["filepath"])
        if not source.is_file():
            raise ValueError("No se encontro el archivo de audio descargado.")

        target = output_dir / (source.stem + ".wav")
        if target.exists():
            raise ValueError(f"El archivo ya existe y no se sobrescribira: {target}")

        try:
            subprocess.run(
                [ffmpeg_executable(), "-nostdin", "-hide_banner", "-loglevel", "error", "-n",
                 "-i", str(source), "-map", "0:a:0", "-vn", "-c:a", "pcm_s24le",
                 "-map_metadata", "0", str(target)],
                check=True, capture_output=True, text=True,
            )
        except FileNotFoundError as exc:
            raise ValueError("Ejecuta Instalar.cmd para preparar FFmpeg antes de convertir a WAV.") from exc
        except subprocess.CalledProcessError as exc:
            target.unlink(missing_ok=True)
            raise ValueError(f"FFmpeg no pudo convertir el audio: {exc.stderr.strip()}") from exc

        return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Descarga audio accesible desde un enlace y lo convierte a WAV PCM de 24 bits.")
    parser.add_argument("url", help="Enlace a una pista individual")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path.cwd(), help="Carpeta de destino (por defecto: carpeta actual)")
    args = parser.parse_args()

    try:
        path = download_wav(args.url, args.output_dir)
    except (ValueError, ImportError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"WAV guardado en: {path}")


if __name__ == "__main__":
    main()
