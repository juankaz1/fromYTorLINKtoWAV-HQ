# fromYTorLINKtoWAV-HQ

Descarga audio o video desde enlaces compatibles con `yt-dlp` y guardalos en tu computadora. La aplicacion para Windows acepta varios enlaces a la vez, muestra el progreso de cada uno y permite escoger una carpeta de destino. Usa solo contenido para el que tengas permisos de acceso y descarga.

## Instalacion facil en Windows

1. En la pagina de este repositorio pulsa **Code > Download ZIP** y extrae la carpeta en un lugar permanente (por ejemplo, Documentos). No abras los `.cmd` directamente dentro del ZIP.
2. Haz doble clic en **Instalar.cmd** dentro de la carpeta extraida. Deja la ventana abierta hasta que diga "Listo"; requiere internet. Detecta Python 3.9 o posterior con Tkinter y, si falta, intenta instalar Python 3.12 para tu usuario con `winget`. Despues prepara `.venv`, instala `yt-dlp` y una copia privada de FFmpeg. No necesitas instalar FFmpeg ni configurar el `PATH` manualmente.
3. Haz doble clic en **Abrir descargador.cmd** para usar la aplicacion.

Si `winget` no esta disponible o falla, instala [Python para Windows](https://www.python.org/downloads/windows/) con pip y Tcl/Tk, y ejecuta **Instalar.cmd** otra vez. Si el instalador acaba de instalar Python pero aun no lo detecta, cierra y vuelve a abrir el Explorador antes de repetirlo. El proceso es seguro de repetir cuando quieras actualizar `yt-dlp`. Es una instalacion local de doble clic, **no un ejecutable autonomo**: necesita Python disponible en el equipo y conexion a internet durante la preparacion.

## Abrir y usar

Haz doble clic en **Abrir descargador.cmd** desde la carpeta extraida tras instalar. Para tenerlo en el escritorio, haz clic derecho en el archivo, elige **Mostrar mas opciones > Enviar a > Escritorio (crear acceso directo)**. No muevas el `.cmd` por separado: el acceso directo debe apuntar al archivo que permanece junto al proyecto.

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