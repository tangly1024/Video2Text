"""Small local web UI for Video2Text."""

from __future__ import annotations

import argparse
import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import webbrowser

from . import convert_to_text

ROOT = Path(__file__).resolve().parent.parent
CLIENT_HTML = Path(getattr(sys, "_MEIPASS", ROOT)) / "clients" / "web-ui.html"


def _read_form_value(form: dict[str, str], name: str, default: str) -> str:
    value = form.get(name, default)
    return str(value).strip() or default


def _read_positive_int(form: dict[str, str], name: str, default: int) -> int:
    raw = _read_form_value(form, name, str(default))
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be a positive integer") from error
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _parse_multipart(
    body: bytes, content_type: str
) -> tuple[dict[str, str], tuple[str, bytes] | None]:
    marker = "boundary="
    if marker not in content_type:
        raise ValueError("missing multipart boundary")
    boundary = content_type.split(marker, 1)[1].split(";", 1)[0].strip().strip('"')
    if not boundary:
        raise ValueError("missing multipart boundary")

    fields: dict[str, str] = {}
    upload: tuple[str, bytes] | None = None
    delimiter = f"--{boundary}".encode("utf-8")
    for part in body.split(delimiter):
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        if part.endswith(b"--"):
            part = part[:-2].rstrip(b"\r\n")
        header_bytes, separator, content = part.partition(b"\r\n\r\n")
        if not separator:
            continue
        headers = header_bytes.decode("utf-8", errors="replace")
        disposition = next(
            (
                line
                for line in headers.split("\r\n")
                if line.lower().startswith("content-disposition:")
            ),
            "",
        )
        name_match = _quoted_header_value(disposition, "name")
        if not name_match:
            continue
        content = content.removesuffix(b"\r\n")
        filename = _quoted_header_value(disposition, "filename")
        if filename:
            upload = (Path(filename).name, content)
        else:
            fields[name_match] = content.decode("utf-8", errors="replace").strip()
    return fields, upload


def _quoted_header_value(header: str, key: str) -> str:
    prefix = f'{key}="'
    start = header.find(prefix)
    if start == -1:
        return ""
    start += len(prefix)
    end = header.find('"', start)
    if end == -1:
        return ""
    return header[start:end]


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Video2TextHandler(BaseHTTPRequestHandler):
    """Serve the shared HTML client and run local conversions."""

    server_version = "Video2TextUI/0.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html", "/web-ui.html"}:
            self._serve_html()
            return
        if self.path == "/api/status":
            _json_response(self, HTTPStatus.OK, {"ok": True, "runtime": "python"})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/convert":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            payload = self._convert_upload()
        except Exception as error:  # noqa: BLE001 - local UI returns user-facing errors.
            _json_response(
                self,
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": html.escape(str(error))},
            )
            return
        _json_response(self, HTTPStatus.OK, payload)

    def _serve_html(self) -> None:
        body = CLIENT_HTML.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _convert_upload(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        form, upload = _parse_multipart(
            self.rfile.read(length),
            self.headers.get("Content-Type", ""),
        )
        if upload is None:
            raise ValueError("请选择音频或视频文件")

        language = _read_form_value(form, "language", "zh-CN")
        segment_length = _read_positive_int(form, "segmentLength", 30)
        workers = _read_positive_int(form, "workers", 5)
        output = Path(_read_form_value(form, "output", "output"))

        source_name, source_content = upload
        suffix = Path(source_name).suffix or ".media"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
            temporary.write(source_content)
            source_path = Path(temporary.name)

        try:
            text_path = convert_to_text(
                source_path,
                output,
                language=language,
                segment_length=segment_length,
                workers=workers,
            )
            text = text_path.read_text(encoding="utf-8")
        finally:
            source_path.unlink(missing_ok=True)

        return {
            "ok": True,
            "path": str(text_path),
            "text": text,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="启动 Video2Text 本地 Web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true", help="不要自动打开浏览器")
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), Video2TextHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Video2Text UI: {url}")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
