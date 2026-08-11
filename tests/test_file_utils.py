from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from video_converter.file_utils import combine_text


class CombineTextTests(unittest.TestCase):
    def test_skips_missing_fragment_and_preserves_order(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "01.txt"
            missing = root / "02.txt"
            third = root / "03.txt"
            target = root / "merged.txt"
            first.write_text("第一段", encoding="utf-8")
            third.write_text("第三段", encoding="utf-8")

            result = combine_text([first, missing, third], target)

            self.assertEqual(result, target)
            self.assertEqual(target.read_text(encoding="utf-8"), "第一段\n第三段\n")


if __name__ == "__main__":
    unittest.main()
