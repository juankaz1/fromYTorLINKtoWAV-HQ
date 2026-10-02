# fromYTorLINKtoWAV-HQ

**Descarga audio WAV y video desde enlaces compatibles con yt-dlp.** Aplicación para Windows con interfaz gráfica, descarga de varios enlaces y selector de calidad de video.

[Español](#español) · [English](#english)

## Español

### Instalar y abrir

1. Pulsa **Code > Download ZIP** en GitHub. Extrae el ZIP a una carpeta permanente; no ejecutes archivos dentro del ZIP.
2. Haz doble clic en **Instalar.cmd**. Necesitas internet; espera hasta que diga **Listo**. Detecta Python o intenta instalarlo, y prepara `yt-dlp` y FFmpeg para esta carpeta.
3. Haz doble clic en **Abrir descargador.cmd**. Para tenerlo en el escritorio, crea un **acceso directo** a ese archivo; deja los archivos originales juntos en la carpeta extraída.

La instalación inicial puede tardar varios minutos. Puedes ejecutar **Instalar.cmd** otra vez si se interrumpe o para actualizar las dependencias. No es un programa autónomo sin instalación: la primera preparación descarga componentes.

### Descargar

1. Pega uno o varios enlaces, incluso dentro de un párrafo, y elige una carpeta de destino existente.
2. Selecciona **Audio WAV** y pulsa **Descargar WAV**, o selecciona **Video**. Para video, pulsa **Consultar calidades** y elige una resolución disponible o **Mejor disponible**; luego pulsa **Descargar video**.
3. Sigue el resultado de cada enlace en el registro. Si uno falla, los demás continúan. Pulsa **Abrir carpeta** al terminar.

Con varios videos, el selector muestra las resoluciones comunes. Si cambias los enlaces, vuelve a consultar las calidades. Los archivos existentes no se sobrescriben. El video puede guardarse como MKV al unir audio y video; convertir audio comprimido a WAV no mejora su calidad original.

### Si la instalación falla

- Si Windows no permite instalar Python automáticamente, instálalo desde [python.org](https://www.python.org/downloads/windows/) con **pip** y **Tcl/Tk**; después ejecuta **Instalar.cmd** de nuevo.
- Si falla la descarga de componentes, comprueba la conexión a internet y repite **Instalar.cmd**. En equipos con restricciones de instalación o red puede requerirse permiso del administrador.
- Si no aparece la ventana, inicia **Abrir descargador.cmd** desde la carpeta extraída y lee el mensaje; completa la preparación con **Instalar.cmd** si falta algún componente.

**Límites:** usa únicamente contenido que tengas derecho a descargar. La compatibilidad de cada sitio depende de `yt-dlp` y puede cambiar. Los enlaces normales de Spotify y Tidal no dan acceso al archivo de audio; la aplicación no evita DRM.

## English

### Install and open

1. Click **Code > Download ZIP** on GitHub. Extract the ZIP to a permanent folder; do not run files from inside the ZIP.
2. Double-click **Instalar.cmd**. An internet connection is required; wait for **Listo** (Done). It detects Python or attempts to install it, then prepares `yt-dlp` and FFmpeg for this folder.
3. Double-click **Abrir descargador.cmd**. For desktop access, create a **shortcut** to this file; keep the original files together in the extracted folder.

The first setup may take several minutes. Run **Instalar.cmd** again if it was interrupted or to update dependencies. This is not a standalone executable: initial setup downloads components.

### Download

1. Paste one or more links, even within a paragraph, and choose an existing destination folder.
2. Select **Audio WAV** and click **Descargar WAV** (Download WAV), or select **Video**. For video, click **Consultar calidades** (Check qualities), choose an available resolution or **Mejor disponible** (Best available), then click **Descargar video** (Download video).
3. Follow each link's result in the log. A failed link does not stop the others. Click **Abrir carpeta** (Open folder) when done.

For multiple videos, the selector shows resolutions shared by all links. Check qualities again after changing the links. Existing files are never overwritten. Video may be saved as MKV when audio and video need merging; converting compressed audio to WAV does not restore lost quality.

### If setup fails

- If Windows cannot install Python automatically, install it from [python.org](https://www.python.org/downloads/windows/) with **pip** and **Tcl/Tk**, then run **Instalar.cmd** again.
- If component downloads fail, check your internet connection and retry **Instalar.cmd**. Restricted computers may require administrator approval.
- If the app does not open, run **Abrir descargador.cmd** from the extracted folder and read its message; use **Instalar.cmd** to repair missing components.

**Limits:** download only content you have permission to use. Site support depends on `yt-dlp` and may change. Ordinary Spotify and Tidal links do not expose the audio file; this app does not bypass DRM.

## Developers / Desarrolladores

The GUI supports both audio and video. The command-line script downloads one link as WAV / La interfaz admite audio y video; el script de terminal descarga un enlace como WAV:

```powershell
.\.venv\Scripts\python.exe .\fromYTorLINKtoWAV-HQ.py "https://www.youtube.com/watch?v=VIDEO_ID" -o "C:\Musica"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```