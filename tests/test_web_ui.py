from video_converter.web_ui import _parse_multipart, _read_positive_int
import unittest


class WebUiTests(unittest.TestCase):
    def test_read_positive_int_accepts_default(self) -> None:
        self.assertEqual(_read_positive_int({}, "workers", 5), 5)

    def test_read_positive_int_rejects_zero(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive integer"):
            _read_positive_int({"workers": "0"}, "workers", 5)

    def test_parse_multipart_reads_fields_and_file(self) -> None:
        body = (
            b"--demo\r\n"
            b'Content-Disposition: form-data; name="language"\r\n\r\n'
            b"zh-CN\r\n"
            b"--demo\r\n"
            b'Content-Disposition: form-data; name="media"; filename="sample.wav"\r\n'
            b"Content-Type: audio/wav\r\n\r\n"
            b"abc\r\n"
            b"--demo--\r\n"
        )

        fields, upload = _parse_multipart(
            body, "multipart/form-data; boundary=demo"
        )

        self.assertEqual(fields["language"], "zh-CN")
        self.assertEqual(upload, ("sample.wav", b"abc"))


if __name__ == "__main__":
    unittest.main()
