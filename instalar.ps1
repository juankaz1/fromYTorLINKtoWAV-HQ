$ErrorActionPreference = 'Stop'
$project = $PSScriptRoot
$venvPython = Join-Path $project '.venv\Scripts\python.exe'
$localFfmpeg = Join-Path $project '.tools\ffmpeg.exe'
$projectPython = Join-Path $project '.runtime\Python312\python.exe'

function Find-Python {
    $candidates = @()
    if (Test-Path $projectPython) {
        $candidates += ,@($projectPython)
    }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $candidates += ,@('py', '-3')
    }
    foreach ($name in @('python', 'python3')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command -and $command.Source -notlike '*\Microsoft\WindowsApps\*') {
            $candidates += ,@($command.Source)
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
        try {
            $version = & $executable @arguments -c 'import sys, tkinter, venv; assert sys.version_info >= (3, 9); print(sys.version.split()[0])' 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Python $version encontrado: $executable $($arguments -join ' ')"
                return ,$candidate
            }
        } catch {
            continue
        }
    }
    return $null
}

function Install-ProjectPython {
    $url = 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe'
    $installer = Join-Path $env:TEMP 'fromYTorLINKtoWAV-HQ-python-3.12.10.exe'
    $target = Split-Path $projectPython
    if (-not [Environment]::Is64BitOperatingSystem) {
        throw 'La instalacion automatica requiere Windows de 64 bits. Instala Python desde python.org/downloads/windows/.'
    }
    Write-Host 'Descargando Python oficial para este proyecto (requiere internet)...'
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
        $signature = Get-AuthenticodeSignature -FilePath $installer
        if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation') {
            throw 'La firma digital del instalador de Python no es valida.'
        }
        Write-Host 'Instalando Python sin modificar el sistema...'
        $arguments = '/quiet InstallAllUsers=0 PrependPath=0 Include_pip=1 Include_tcltk=1 Include_test=0 TargetDir="' + $target + '"'
        $process = Start-Process -FilePath $installer -ArgumentList $arguments -PassThru
        if (-not $process.WaitForExit(300000)) {
            $process.Kill()
            throw 'La instalacion automatica de Python no respondio. Instala Python desde https://www.python.org/downloads/windows/ y ejecuta Instalar.cmd otra vez.'
        }
        if ($process.ExitCode -ne 0 -or -not (Test-Path $projectPython)) {
            throw "La instalacion de Python fallo (codigo $($process.ExitCode)). Instala Python desde https://www.python.org/downloads/windows/ y repite Instalar.cmd."
        }
    } finally {
        Remove-Item $installer -Force -ErrorAction SilentlyContinue
    }
}

try {
    $python = Find-Python
    if (-not $python) {
        Write-Host 'No se encontro Python 3.9+ con Tkinter.'
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host 'Intentando instalar Python 3.12 con winget...'
            try {
                & winget install --id Python.Python.3.12 --exact --source winget --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity
            } catch {
                Write-Host 'winget no pudo completar la instalacion; usando instalador oficial.'
            }
            $python = Find-Python
        }
        if (-not $python) {
            Install-ProjectPython
            $python = Find-Python
        }
        if (-not $python) {
            throw 'Python no quedo disponible. Comprueba la conexion y vuelve a ejecutar Instalar.cmd.'
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