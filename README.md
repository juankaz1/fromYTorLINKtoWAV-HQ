# fromYTorLINKtoWAV-HQ

Descarga audio o video desde enlaces compatibles con `yt-dlp` y guardalos en tu computadora. La aplicacion para Windows acepta varios enlaces a la vez, muestra el progreso de cada uno y permite escoger una carpeta de destino. Usa solo contenido para el que tengas permisos de acceso y descarga.

## Instalar en Windows

1. En la pagina de este repositorio, pulsa **Code > Download ZIP** y extrae el ZIP en una carpeta permanente (por ejemplo, Documentos). Tambien puedes clonarlo con Git. No ejecutes el lanzador desde dentro del ZIP.
2. Instala [Python 3.9 o posterior](https://www.python.org/downloads/) y [FFmpeg](https://ffmpeg.org/download.html). FFmpeg debe estar en el `PATH`. Abre una nueva ventana de PowerShell y comprueba `py -3 --version` y `ffmpeg -version`.
3. Abre la carpeta extraida; escribe `powershell` en la barra de direcciones del Explorador de archivos y pulsa Enter. En esa terminal ejecuta una sola vez:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade yt-dlp
```

Si tu equipo no reconoce `py`, usa `python -m venv .venv` en el primer comando. Para actualizar la compatibilidad con sitios que cambian, repite el comando de `pip install --upgrade yt-dlp`.

## Abrir y usar

Haz doble clic en **Abrir descargador.cmd** desde la carpeta extraida. El lanzador usa el Python de `.venv`, por lo que ese entorno debe existir. Para tenerlo en el escritorio, haz clic derecho en el archivo, elige **Mostrar mas opciones > Enviar a > Escritorio (crear acceso directo)**. No muevas el archivo `.cmd` por separado: el acceso directo debe apuntar al archivo que permanece junto al proyecto.

1. Pega uno o varios enlaces en el campo de texto, incluso dentro de un parrafo o separados por comas, espacios o saltos de linea. Los enlaces repetidos se procesan una sola vez.
2. Elige una carpeta existente con **Examinar...**, escribela en el campo de destino o escoge una usada recientemente.
3. Para extraer audio, selecciona **Audio WAV** y pulsa **Descargar WAV**. El archivo se convierte a PCM de 24 bits, manteniendo la frecuencia de muestreo de origen.
4. Para guardar video, selecciona **Video**. Pulsa **Consultar calidades** para ver las resoluciones disponibles; con varios enlaces aparecen solo las comunes a todos. Elige una resolucion o deja **Mejor disponible** para obtener la mejor de cada enlace. Pulsa **Descargar video**.

La barra y el registro muestran el estado y los errores de cada enlace; si uno falla, los siguientes continuan. Al terminar puedes pulsar **Abrir carpeta**. Si cambias los enlaces despues de consultar calidades, vuelve a consultarlas antes de elegir una resolucion concreta. Nunca se sobrescribe un archivo que ya existe.

Los videos conservan su contenedor si audio y video vienen juntos, o se guardan como MKV cuando FFmpeg debe unir pistas; no se recomprimen para forzar MP4. Convertir audio comprimido a WAV **no recupera calidad perdida**: la calidad final depende del origen.

## Linea de comandos

La interfaz grafica es la opcion para audio y video. El script de terminal permite descargar una pista individual como WAV:

```powershell
.\.venv\Scripts\python.exe .\fromYTorLINKtoWAV-HQ.py "https://www.youtube.com/watch?v=ID_DEL_VIDEO" -o "C:\Musica"
```

La carpeta de destino debe existir; si omites `-o`, se usa la carpeta actual. Usa `--help` para ver sus opciones.

## Limitaciones

La disponibilidad depende de cada sitio y puede cambiar. Se admiten enlaces publicos compatibles con `yt-dlp`, por ejemplo ciertos videos de YouTube y pistas de SoundCloud. Spotify y Tidal no proporcionan el archivo de sus canciones mediante enlaces publicos ordinarios. Esta herramienta no descifra DRM ni graba streams protegidos.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```