from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pydub import AudioSegment

from video_converter.voice_utils import split_voice_file


class SplitVoiceFileTests(unittest.TestCase):
    def test_honors_split_length_without_empty_tail(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "sample.wav"
            exported = AudioSegment.silent(duration=6000).export(source, format="wav")
            exported.close()

            parts = split_voice_file(source, "sample", root, split_length=3)

            self.assertEqual(len(parts), 2)
            self.assertTrue(all(Path(part).stat().st_size > 44 for part in parts))


if __name__ == "__main__":
    unittest.main()
