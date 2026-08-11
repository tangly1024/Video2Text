from pathlib import Path
from typing import Iterable

from .log_utils import get_logger

log = get_logger("files")


def get_file_name_and_extension(file_path: str | Path) -> tuple[str, str]:
    """Return ``(stem, suffix)`` for compatibility with the original API."""
    path = Path(file_path)
    return path.stem, path.suffix


def combine_text(
    from_text_array: Iterable[str | Path], target_text_file: str | Path
) -> Path:
    """Merge existing UTF-8 text fragments in order, skipping failed fragments."""
    fragments: list[str] = []
    for text_file in map(Path, from_text_array):
        if text_file.is_file():
            fragments.append(text_file.read_text(encoding="utf-8").rstrip("\r\n"))
        else:
            log.warning("跳过不存在的转写片段: %s", text_file)

    target = Path(target_text_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(fragment for fragment in fragments if fragment)
    target.write_text(f"{content}\n" if content else "", encoding="utf-8")
    return target
