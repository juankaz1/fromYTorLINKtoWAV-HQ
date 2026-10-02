$ErrorActionPreference = 'Stop'
$project = $PSScriptRoot
$venvPython = Join-Path $project '.venv\Scripts\python.exe'
$localFfmpeg = Join-Path $project '.tools\ffmpeg.exe'

function Find-Python {
    $candidates = @()
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $candidates += ,@('py', '-3')
    }
    foreach ($name in @('python', 'python3')) {
        if (Get-Command $name -ErrorAction SilentlyContinue) {
            $candidates += ,@($name)
        }
    }
    $localPython = Join-Path $env:LOCALAPPDATA 'Programs\Python'
    if (Test-Path $localPython) {
        Get-ChildItem $localPython -Directory -Filter 'Python3*' | ForEach-Object {
            $candidates += ,@((Join-Path $_.FullName 'python.exe'))
        }
    }
    foreach ($candidate in $candidates) {
        $executable = $candidate[0]
        $arguments = @($candidate | Select-Object -Skip 1)
        $version = & $executable @arguments -c 'import sys, tkinter, venv; assert sys.version_info >= (3, 9); print(sys.version.split()[0])' 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python $version encontrado: $executable $($arguments -join ' ')"
            return ,$candidate
        }
    }
    return $null
}

try {
    $python = Find-Python
    if (-not $python) {
        Write-Host 'No se encontro Python 3.9+ con Tkinter. Intentando instalar Python 3.12 con winget...'
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            throw 'Instala Python desde https://www.python.org/downloads/windows/ (incluye pip y Tcl/Tk) y vuelve a ejecutar Instalar.cmd.'
        }
        & winget install --id Python.Python.3.12 --exact --source winget --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity
        if ($LASTEXITCODE -ne 0) {
            throw 'winget no pudo instalar Python. Instalalo desde https://www.python.org/downloads/windows/ y vuelve a ejecutar Instalar.cmd.'
        }
        $python = Find-Python
        if (-not $python) {
            throw 'Python se instalo, pero aun no se encuentra. Cierra y abre el Explorador de archivos, luego repite Instalar.cmd.'
        }
    }

    if (-not (Test-Path $venvPython)) {
        Write-Host 'Creando entorno privado .venv...'
        $executable = $python[0]
        $arguments = @($python | Select-Object -Skip 1)
        & $executable @arguments -m venv (Join-Path $project '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear .venv. Comprueba que Python incluya venv y pip.' }
    }

    Write-Host 'Instalando yt-dlp y FFmpeg local (requiere internet)...'
    & $venvPython -m pip install --upgrade 'yt-dlp>=2025.1.0' imageio-ffmpeg
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron descargar las dependencias. Comprueba la conexion a internet.' }

    New-Item -ItemType Directory -Path (Split-Path $localFfmpeg) -Force | Out-Null
    & $venvPython -c 'import imageio_ffmpeg, shutil, sys; shutil.copy2(imageio_ffmpeg.get_ffmpeg_exe(), sys.argv[1])' $localFfmpeg
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar FFmpeg local.' }
    & $localFfmpeg -version | Select-Object -First 1
    if ($LASTEXITCODE -ne 0) { throw 'FFmpeg local no funciona.' }
    Write-Host 'Instalacion terminada. No necesitas configurar el PATH.'
    exit 0
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}