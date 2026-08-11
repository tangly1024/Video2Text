"""Video2Text public API."""

from pathlib import Path

from .file_utils import combine_text
from .log_utils import get_logger
from .voice_utils import (
    convert_audios_to_text,
    convert_media_to_wave,
    split_voice_file,
)

log = get_logger("pipeline")


def convert_to_text(
    source_media_path: str | Path,
    output_path: str | Path = "./output",
    *,
    language: str = "zh-CN",
    segment_length: int = 30,
    workers: int = 5,
) -> Path:
    """Transcribe one media file and return the merged UTF-8 text path."""
    source = Path(source_media_path).expanduser()
    if not source.is_file():
        raise FileNotFoundError(f"输入文件不存在: {source}")
    if segment_length <= 0:
        raise ValueError("segment_length 必须大于 0")
    if workers <= 0:
        raise ValueError("workers 必须大于 0")

    project_path = Path(output_path).expanduser() / source.stem
    project_path.mkdir(parents=True, exist_ok=True)

    wave_path = convert_media_to_wave(source, project_path)
    audio_parts = split_voice_file(
        wave_path,
        source.stem,
        project_path,
        split_length=segment_length,
    )
    text_parts = convert_audios_to_text(
        audio_parts,
        max_convert_thread=workers,
        language=language,
    )
    if not text_parts:
        raise RuntimeError("没有任何音频片段转写成功，请检查网络、语言参数和日志")

    target = project_path / f"{source.stem}.txt"
    combine_text(text_parts, target)
    log.info("转写完成: %s", target)
    return target


__all__ = ["convert_to_text"]
