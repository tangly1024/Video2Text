"""Backward-compatible executable entry point."""

from video_converter.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
