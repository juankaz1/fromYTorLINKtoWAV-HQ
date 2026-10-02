import importlib.util
import json
import os
import queue
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk


SCRIPT = Path(__file__).with_name("fromYTorLINKtoWAV-HQ.py")
spec = importlib.util.spec_from_file_location("audio_downloader", SCRIPT)
downloader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloader)

RECENTS_FILE = Path(os.environ.get("APPDATA", Path.home())) / "fromYTorLINKtoWAV-HQ" / "recent.json"
DEFAULT_FOLDER = Path.home() / "Music" / "fromYTorLINKtoWAV-HQ"


def extract_links(text: str) -> list[str]:
    matches = re.findall(r"https?://[^\s<>\"',;]+", text, flags=re.IGNORECASE)
    return list(dict.fromkeys(match.rstrip(".!)]}") for match in matches))


def load_recents() -> list[str]:
    try:
        folders = json.loads(RECENTS_FILE.read_text(encoding="utf-8"))
        if isinstance(folders, list):
            return [folder for folder in folders if isinstance(folder, str) and Path(folder).is_dir()][:8]
    except (OSError, ValueError):
        pass
    return []


def save_recent(folder: Path) -> list[str]:
    folders = [str(folder)] + [previous for previous in load_recents() if previous != str(folder)]
    RECENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RECENTS_FILE.write_text(json.dumps(folders[:8], ensure_ascii=False), encoding="utf-8")
    return folders[:8]


def query_qualities(links: list[str], report) -> None:
    common = None
    failed = False
    for index, link in enumerate(links, start=1):
        report("quality_start", index, link)
        try:
            qualities = set(downloader.available_video_qualities(link))
            if not qualities:
                raise ValueError("No hay formatos de video disponibles.")
        except Exception as exc:
            failed = True
            report("quality_error", index, f"{link}: {exc}")
        else:
            common = qualities if common is None else common & qualities
            report("quality_result", index, ", ".join(f"{height}p" for height in sorted(qualities, reverse=True)))
    report("quality_done", sorted(common or [], reverse=True) if not failed else [], failed)


def download_batch(links: list[str], destination: Path, report, mode: str = "wav", height=None) -> None:
    successes = 0
    for index, link in enumerate(links, start=1):
        report("start", index, link)
        try:
            saved = (downloader.download_video(link, destination, height) if mode == "video"
                     else downloader.download_wav(link, destination))
        except Exception as exc:
            report("error", index, f"{link}: {exc}")
        else:
            successes += 1
            report("success", index, str(saved))
    report("done", successes, len(links))


def main() -> None:
    try:
        DEFAULT_FOLDER.mkdir(parents=True, exist_ok=True)
        initial_folder = DEFAULT_FOLDER
    except OSError:
        initial_folder = Path.home()
    root = tk.Tk()
    root.title("Enlaces a WAV y video")
    root.geometry("810x610")
    root.minsize(640, 500)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame = ttk.Frame(root, padding=20)
    frame.grid(sticky="nsew")
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(1, weight=1)
    frame.rowconfigure(8, weight=1)

    folder = tk.StringVar(value=str(initial_folder))
    mode = tk.StringVar(value="wav")
    quality = tk.StringVar(value="Mejor disponible")
    status = tk.StringVar(value="Listo")
    result = queue.Queue()
    total = 0
    current_destination = None
    consulted_links = None

    ttk.Label(frame, text="Enlaces").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
    link_input = scrolledtext.ScrolledText(frame, height=7, wrap="word")
    link_input.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(0, 12))
    ttk.Label(frame, text="Formato").grid(row=2, column=0, sticky="w", pady=(0, 10))
    ttk.Label(frame, text="Calidad").grid(row=3, column=0, sticky="w", pady=(0, 10))
    quality_select = ttk.Combobox(frame, textvariable=quality, values=["Mejor disponible"], state="disabled")
    quality_select.grid(row=3, column=1, sticky="ew", pady=(0, 10))
    ttk.Label(frame, text="Guardar en").grid(row=4, column=0, sticky="w", padx=(0, 12), pady=(0, 10))
    folders = ttk.Combobox(frame, textvariable=folder, values=load_recents(), width=57)
    folders.grid(row=4, column=1, sticky="ew", pady=(0, 10))

    def browse() -> None:
        chosen = filedialog.askdirectory(initialdir=folder.get() if Path(folder.get()).is_dir() else str(Path.home()))
        if chosen:
            folder.set(chosen)

    ttk.Button(frame, text="Examinar...", command=browse).grid(row=4, column=2, padx=(8, 0), pady=(0, 10))
    ttk.Label(frame, textvariable=status, wraplength=740).grid(row=5, column=0, columnspan=3, sticky="w", pady=(4, 6))
    progress = ttk.Progressbar(frame, maximum=1, mode="determinate")
    progress.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 12))
    ttk.Label(frame, text="Resultados").grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 6))
    log = scrolledtext.ScrolledText(frame, height=9, wrap="word", state="disabled")
    log.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(0, 12))

    def set_mode() -> None:
        is_video = mode.get() == "video"
        quality_select.config(state="readonly" if is_video else "disabled")
        quality_button.config(state="normal" if is_video else "disabled")
        download_button.config(text="Descargar video" if is_video else "Descargar WAV")

    audio_button = ttk.Radiobutton(frame, text="Audio WAV", variable=mode, value="wav", command=set_mode)
    audio_button.grid(row=2, column=1, sticky="w", pady=(0, 10))
    video_button = ttk.Radiobutton(frame, text="Video", variable=mode, value="video", command=set_mode)
    video_button.grid(row=2, column=2, sticky="w", pady=(0, 10))

    def write_log(message: str) -> None:
        log.config(state="normal")
        log.insert("end", message + "\n")
        log.see("end")
        log.config(state="disabled")

    def poll() -> None:
        try:
            event, index, value = result.get_nowait()
        except queue.Empty:
            root.after(150, poll)
            return
        if event == "start":
            status.set(f"Descargando {index}/{total}: {value}")
            write_log(f"[{index}/{total}] Descargando: {value}")
        elif event == "success":
            progress["value"] = index
            write_log(f"[{index}/{total}] Guardado: {value}")
        elif event == "error":
            progress["value"] = index
            write_log(f"[{index}/{total}] Error: {value}")
        elif event == "quality_start":
            status.set(f"Consultando calidades {index}/{total}: {value}")
        elif event == "quality_result":
            progress["value"] = index
            write_log(f"[{index}/{total}] Calidades: {value}")
        elif event == "quality_error":
            progress["value"] = index
            write_log(f"[{index}/{total}] Error al consultar: {value}")
        elif event == "quality_done":
            quality_select.config(values=["Mejor disponible"] + [f"{height}p" for height in index])
            quality.set("Mejor disponible")
            status.set("No se pudieron consultar todos los enlaces; revisa el registro." if value else
                       f"{len(index)} resoluciones comunes disponibles para {total} enlace(s).")
            download_button.config(state="normal")
            audio_button.config(state="normal")
            video_button.config(state="normal")
            set_mode()
            return
        elif event == "done":
            status.set(f"Completado: {index} de {value} archivos guardados; {value - index} errores.")
            download_button.config(state="normal")
            audio_button.config(state="normal")
            video_button.config(state="normal")
            set_mode()
            if index:
                open_button.config(state="normal", command=lambda: os.startfile(current_destination))
                try:
                    folders.config(values=save_recent(current_destination))
                except OSError:
                    pass
            return
        root.after(150, poll)

    def consult() -> None:
        nonlocal total, consulted_links
        links = extract_links(link_input.get("1.0", "end"))
        if not links:
            messagebox.showwarning("Faltan enlaces", "Pega uno o varios enlaces HTTP o HTTPS.")
            return
        total = len(links)
        consulted_links = tuple(links)
        quality.set("Mejor disponible")
        quality_select.config(values=["Mejor disponible"], state="disabled")
        download_button.config(state="disabled")
        quality_button.config(state="disabled")
        audio_button.config(state="disabled")
        video_button.config(state="disabled")
        progress.config(maximum=total, value=0)
        log.config(state="normal")
        log.delete("1.0", "end")
        log.config(state="disabled")
        status.set(f"Consultando {total} enlace(s)...")
        threading.Thread(target=query_qualities, args=(links, lambda *event: result.put(event)), daemon=True).start()
        root.after(150, poll)

    def start() -> None:
        nonlocal total, current_destination
        links = extract_links(link_input.get("1.0", "end"))
        destination = Path(folder.get().strip().strip('"')).expanduser()
        if not links:
            messagebox.showwarning("Faltan enlaces", "Pega uno o varios enlaces HTTP o HTTPS.")
            link_input.focus_set()
            return
        if not destination.is_dir():
            messagebox.showwarning("Carpeta no encontrada", "Elige o escribe una carpeta que ya exista.")
            return
        height = None
        if mode.get() == "video" and quality.get() != "Mejor disponible":
            if tuple(links) != consulted_links:
                messagebox.showwarning("Calidad desactualizada", "Los enlaces cambiaron. Consulta las calidades de nuevo.")
                return
            height = int(quality.get()[:-1])
        total = len(links)
        current_destination = destination
        download_button.config(state="disabled")
        quality_button.config(state="disabled")
        quality_select.config(state="disabled")
        audio_button.config(state="disabled")
        video_button.config(state="disabled")
        open_button.config(state="disabled")
        progress.config(maximum=total, value=0)
        log.config(state="normal")
        log.delete("1.0", "end")
        log.config(state="disabled")
        status.set(f"Preparando {total} enlace(s)...")
        threading.Thread(target=download_batch, args=(links, destination, lambda *event: result.put(event), mode.get(), height), daemon=True).start()
        root.after(150, poll)

    download_button = ttk.Button(frame, text="Descargar WAV", command=start)
    download_button.grid(row=9, column=1, sticky="e")
    quality_button = ttk.Button(frame, text="Consultar calidades", command=consult, state="disabled")
    quality_button.grid(row=3, column=2, padx=(8, 0), pady=(0, 10))
    open_button = ttk.Button(frame, text="Abrir carpeta", state="disabled")
    open_button.grid(row=9, column=2, padx=(8, 0))
    root.bind("<Control-Return>", lambda event: start() if str(download_button["state"]) == "normal" else None)
    link_input.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()