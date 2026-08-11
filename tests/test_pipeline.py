from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from video_converter import convert_to_text
from video_converter.cli import main


class PipelineTests(unittest.TestCase):
    def test_uses_requested_output_and_returns_merged_text(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "meeting.wav"
            source.touch()
            fragment = root / "fragment.txt"
            fragment.write_text("hello", encoding="utf-8")

            with (
                patch(
                    "video_converter.convert_media_to_wave", return_value="audio.wav"
                ),
                patch("video_converter.split_voice_file", return_value=["part.wav"]),
                patch(
                    "video_converter.convert_audios_to_text",
                    return_value=[str(fragment)],
                ),
            ):
                result = convert_to_text(source, root / "custom-output")

            self.assertEqual(
                result, root / "custom-output" / "meeting" / "meeting.txt"
            )
            self.assertEqual(result.read_text(encoding="utf-8"), "hello\n")

    def test_rejects_invalid_runtime_limits(self) -> None:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "audio.wav"
            source.touch()
            with self.assertRaises(ValueError):
                convert_to_text(source, segment_length=0)
            with self.assertRaises(ValueError):
                convert_to_text(source, workers=0)

    def test_rejects_empty_transcription(self) -> None:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "audio.wav"
            source.touch()
            with (
                patch(
                    "video_converter.convert_media_to_wave", return_value="audio.wav"
                ),
                patch("video_converter.split_voice_file", return_value=["part.wav"]),
                patch("video_converter.convert_audios_to_text", return_value=[]),
                self.assertRaises(RuntimeError),
            ):
                convert_to_text(source)

    def test_cli_returns_nonzero_for_missing_input(self) -> None:
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as raised:
            main(["missing.wav"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
