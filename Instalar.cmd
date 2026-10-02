@echo off
setlocal
echo Preparando fromYTorLINKtoWAV-HQ...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"
if errorlevel 1 (
    echo.
    echo No se pudo completar la instalacion. Revisa el mensaje anterior.
    pause
    exit /b 1
)
echo.
echo Listo. Haz doble clic en "Abrir descargador.cmd" para iniciar.
pause