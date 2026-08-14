"""PyInstaller-friendly launcher for the local web UI."""

from video_converter.web_ui import main


if __name__ == "__main__":
    raise SystemExit(main())
