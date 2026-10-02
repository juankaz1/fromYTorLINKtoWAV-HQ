import importlib.util
import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "fromYTorLINKtoWAV-HQ.py"
spec = importlib.util.spec_from_file_location("audio_downloader", SCRIPT)
downloader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloader)


class DownloadTests(unittest.TestCase):
    def test_prefers_local_ffmpeg_when_installed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            local = Path(temp_dir) / ".tools" / "ffmpeg.exe"
            local.parent.mkdir()
            local.touch()
            with patch.object(downloader, "__file__", str(Path(temp_dir) / SCRIPT.name)):
                self.assertEqual(downloader.ffmpeg_executable(), str(local))
                self.assertEqual(downloader.ffmpeg_options(), {"ffmpeg_location": str(local)})
                local.unlink()
                self.assertEqual(downloader.ffmpeg_executable(), "ffmpeg")
                self.assertEqual(downloader.ffmpeg_options(), {})

    def test_available_video_qualities_ignore_audio_and_duplicates(self):
        import yt_dlp

        class FakeYoutubeDL:
            def __init__(self, options):
                self.options = options

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def extract_info(self, url, download):
                self_test.assertFalse(download)
                return {"formats": [
                    {"vcodec": "none", "height": None},
                    {"vcodec": "vp9", "height": 1080},
                    {"vcodec": "avc1", "height": 720},
                    {"vcodec": "vp9", "height": 720},
                ]}

        self_test = self
        with patch.object(yt_dlp, "YoutubeDL", FakeYoutubeDL):
            self.assertEqual(downloader.available_video_qualities("https://example.com/video"), [1080, 720])

    def test_download_video_exact_quality_and_no_overwrite(self):
        import yt_dlp

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            class FakeYoutubeDL:
                def __init__(self, options):
                    self.options = options

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

                def extract_info(self, url, download):
                    self_test.assertTrue(download)
                    self_test.assertEqual(self.options["format"], "bv[height=720]+ba/b[height=720]")
                    self_test.assertEqual(self.options["merge_output_format"], "mkv")
                    source = Path(self.options["outtmpl"]).parent / "clip [id].mkv"
                    source.write_bytes(b"video")
                    return {"filepath": str(source)}

            self_test = self
            with patch.object(yt_dlp, "YoutubeDL", FakeYoutubeDL):
                target = downloader.download_video("https://example.com/video", output_dir, 720)
                self.assertEqual(target.read_bytes(), b"video")
                with self.assertRaisesRegex(ValueError, "no se sobrescribira"):
                    downloader.download_video("https://example.com/video", output_dir, 720)

    def test_common_video_qualities_for_multiple_links(self):
        gui = runpy.run_path(str(SCRIPT.with_name("fromYTorLINKtoWAV-HQ-gui.pyw")))
        events = []
        with patch.object(gui["downloader"], "available_video_qualities", side_effect=[
            [1080, 720], [720, 480],
        ]):
            gui["query_qualities"](["https://one", "https://two"], lambda *event: events.append(event))
        self.assertEqual(events[-1], ("quality_done", [720], False))

        with patch.object(gui["downloader"], "available_video_qualities", side_effect=[
            [1080, 720], ValueError("no hay video"),
        ]):
            gui["query_qualities"](["https://one", "https://two"], lambda *event: events.append(event))
        self.assertEqual(events[-1], ("quality_done", [], True))

    def test_batch_downloads_video_at_selected_height(self):
        gui = runpy.run_path(str(SCRIPT.with_name("fromYTorLINKtoWAV-HQ-gui.pyw")))
        events = []
        with patch.object(gui["downloader"], "download_video", return_value=Path("clip.mkv")) as download:
            gui["download_batch"](["https://one"], Path.cwd(), lambda *event: events.append(event), "video", 720)
        download.assert_called_once_with("https://one", Path.cwd(), 720)
        self.assertEqual(events[-1], ("done", 1, 1))

    def test_extract_links_from_paragraph_and_deduplicate(self):
        gui = runpy.run_path(str(SCRIPT.with_name("fromYTorLINKtoWAV-HQ-gui.pyw")))
        pasted = (
            "Escucha https://youtu.be/cc5BlNbKrBo?si=abc, tambien "
            "(https://soundcloud.com/artist/song).\n"
            "De nuevo: https://youtu.be/cc5BlNbKrBo?si=abc"
        )
        self.assertEqual(gui["extract_links"](pasted), [
            "https://youtu.be/cc5BlNbKrBo?si=abc",
            "https://soundcloud.com/artist/song",
        ])
        self.assertEqual(gui["extract_links"]("texto sin enlaces"), [])

    def test_batch_continues_after_failed_link(self):
        gui = runpy.run_path(str(SCRIPT.with_name("fromYTorLINKtoWAV-HQ-gui.pyw")))
        events = []
        with patch.object(gui["downloader"], "download_wav", side_effect=[
            Path("first.wav"), ValueError("no disponible"), Path("third.wav"),
        ]) as download:
            gui["download_batch"](["https://one", "https://two", "https://three"], Path.cwd(),
                                  lambda *event: events.append(event))
        self.assertEqual(download.call_count, 3)
        self.assertEqual([event[0] for event in events], [
            "start", "success", "start", "error", "start", "success", "done",
        ])
        self.assertIn("no disponible", events[3][2])
        self.assertEqual(events[-1], ("done", 2, 3))

    def test_recent_destinations(self):
        gui = runpy.run_path(str(SCRIPT.with_name("fromYTorLINKtoWAV-HQ-gui.pyw")))
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first"
            second = Path(temp_dir) / "second"
            first.mkdir()
            second.mkdir()
            save_recent = gui["save_recent"]
            load_recents = gui["load_recents"]
            with patch.dict(save_recent.__globals__, {"RECENTS_FILE": Path(temp_dir) / "recent.json"}):
                save_recent(first)
                save_recent(second)
                self.assertEqual(load_recents(), [str(second), str(first)])
                save_recent(first)
                self.assertEqual(load_recents(), [str(first), str(second)])

    def test_invalid_url(self):
        with self.assertRaisesRegex(ValueError, "HTTP o HTTPS"):
            downloader.download_wav("file:///local/song.mp3", Path.cwd())

    def test_protected_service(self):
        with self.assertRaisesRegex(ValueError, "DRM"):
            downloader.download_wav("https://open.spotify.com/track/example", Path.cwd())

    def test_conversion_preserves_sample_rate_and_does_not_overwrite(self):
        import yt_dlp

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            source = output_dir / "source.flac"
            subprocess.run(
                ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                 "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=0.1",
                 "-c:a", "flac", str(source)],
                check=True,
            )

            class FakeYoutubeDL:
                def __init__(self, options):
                    self.options = options

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

                def extract_info(self, url, download):
                    self_test.assertTrue(download)
                    self_test.assertEqual(self.options["format"], "bestaudio/best")
                    return {"requested_downloads": [{"filepath": str(source)}]}

            self_test = self
            with patch.object(yt_dlp, "YoutubeDL", FakeYoutubeDL):
                target = downloader.download_wav("https://example.com/song", output_dir)
                self.assertTrue(target.is_file())
                probe = subprocess.run(
                    ["ffprobe", "-v", "error", "-select_streams", "a:0",
                     "-show_entries", "stream=codec_name,sample_rate,bits_per_sample",
                     "-of", "default=noprint_wrappers=1", str(target)],
                    check=True, capture_output=True, text=True,
                )
                self.assertIn("pcm_s24le", probe.stdout)
                self.assertIn("48000", probe.stdout)
                self.assertIn("24", probe.stdout)
                with self.assertRaisesRegex(ValueError, "no se sobrescribira"):
                    downloader.download_wav("https://example.com/song", output_dir)


if __name__ == "__main__":
    unittest.main()