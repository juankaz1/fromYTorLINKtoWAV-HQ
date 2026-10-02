@echo off
setlocal
if not exist "%~dp0.venv\Scripts\pythonw.exe" (
    echo Falta la instalacion. Haz doble clic en "Instalar.cmd" primero.
    pause
    exit /b 1
)
if not exist "%~dp0.tools\ffmpeg.exe" (
    echo Falta FFmpeg local. Haz doble clic en "Instalar.cmd" para completar la preparacion.
    pause
    exit /b 1
)
"%~dp0.venv\Scripts\python.exe" -c "import yt_dlp" >nul 2>&1
if errorlevel 1 (
    echo Falta yt-dlp. Haz doble clic en "Instalar.cmd" para completar la preparacion.
    pause
    exit /b 1
)
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0fromYTorLINKtoWAV-HQ-gui.pyw"