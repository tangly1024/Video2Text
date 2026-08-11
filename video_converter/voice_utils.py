"""Media normalization, splitting, and Google Web Speech transcription."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import threading
from typing import Iterable

from pydub import AudioSegment
import speech_recognition as sr

from .log_utils import get_logger

log = get_logger("audio")
SUPPORTED_EXTENSIONS = {".flv", ".m4a", ".mp3", ".mp4", ".wav"}


def split_voice_file(
    voice_file: str | Path,
    file_name_prefix: str,
    output_path: str | Path = "./",
    split_length: int = 30,
) -> list[str]:
    """Split a WAV file into chunks with a two-second context overlap."""
    if split_length <= 0:
        raise ValueError("split_length 必须大于 0")

    with Path(voice_file).open("rb") as source:
        audio = AudioSegment.from_wav(source)
    split_folder = Path(output_path) / "split"
    split_folder.mkdir(parents=True, exist_ok=True)
    segment_ms = split_length * 1000
    overlap_ms = 2000
    result: list[str] = []

    for index, start in enumerate(range(0, len(audio), segment_ms), start=1):
        target = split_folder / f"{file_name_prefix}-{index:02d}.wav"
        exported = audio[
            start : min(start + segment_ms + overlap_ms, len(audio))
        ].export(target, format="wav")
        exported.close()
        result.append(str(target))

    log.info("音频已分为 %s 个 %ss 片段", len(result), split_length)
    return result


def convert_audios_to_text(
    file_array: Iterable[str | Path],
    max_convert_thread: int = 5,
    jump_exists_file: bool = True,
    language: str = "zh-CN",
) -> list[str]:
    """Transcribe audio chunks concurrently and return successful text paths."""
    if max_convert_thread <= 0:
        raise ValueError("max_convert_thread 必须大于 0")

    def convert(voice_file: str | Path) -> str | None:
        destination_path = Path(voice_file).with_suffix(".txt")
        destination = str(destination_path)
        if (
            jump_exists_file
            and destination_path.is_file()
            and destination_path.stat().st_size > 0
        ):
            log.info("复用已有转写片段: %s", destination)
            return destination
        return convert_by_google(voice_file, destination, language=language)

    files = list(file_array)
    with ThreadPoolExecutor(max_workers=max_convert_thread) as executor:
        results = executor.map(convert, files)
    return [result for result in results if result]


def convert_by_google(
    voice_file: str | Path,
    dst_file_name: str | Path,
    semaphore: threading.Semaphore | None = None,
    recognizer: sr.Recognizer | None = None,
    language: str = "zh-CN",
) -> str | None:
    """Transcribe one WAV file through SpeechRecognition's Google backend."""
    if semaphore:
        semaphore.acquire()
    try:
        recognizer = recognizer or sr.Recognizer()
        with sr.AudioFile(str(voice_file)) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=language)
        destination = Path(dst_file_name)
        destination.write_text(text, encoding="utf-8")
        return str(destination)
    except sr.UnknownValueError:
        log.warning("无法识别音频片段: %s", voice_file)
    except sr.RequestError as error:
        log.error("Google 语音服务请求失败 (%s): %s", voice_file, error)
    except (OSError, ValueError) as error:
        log.error("音频片段处理失败 (%s): %s", voice_file, error)
    finally:
        if semaphore:
            semaphore.release()
    return None


def get_audio_duration(voice_file: str | Path) -> int:
    """Return whole seconds for an audio file."""
    with Path(voice_file).open("rb") as source:
        return len(AudioSegment.from_file(source)) // 1000


def convert_media_to_wave(
    source_file: str | Path, target_folder: str | Path
) -> str:
    """Normalize a supported media file to WAV using pydub/FFmpeg."""
    source = Path(source_file)
    if not source.is_file():
        raise FileNotFoundError(f"输入文件不存在: {source}")
    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"不支持 {source.suffix or '无扩展名'}；支持: {supported}")

    target_folder = Path(target_folder)
    target_folder.mkdir(parents=True, exist_ok=True)
    target = target_folder / f"{source.stem}.wav"
    if target.exists():
        return str(target)
    if source.suffix.lower() == ".wav":
        shutil.copy2(source, target)
    else:
        with source.open("rb") as media:
            audio = AudioSegment.from_file(media)
        exported = audio.export(target, format="wav")
        exported.close()
    return str(target)


def mp3_2_wav(
    source_mp3_file: str | Path,
    target_folder: str | Path,
    jump_exist_file: bool = True,
) -> str:
    """Backward-compatible wrapper for MP3 conversion."""
    return convert_media_to_wave(source_mp3_file, target_folder)


def trans_m4a_to_wav(
    source_m4a_file: str | Path,
    target_folder: str | Path,
    jump_exist_file: bool = True,
) -> str:
    """Backward-compatible wrapper for M4A conversion."""
    return convert_media_to_wave(source_m4a_file, target_folder)


def video_2_mp3(
    source_mp4_file: str | Path,
    target_folder: str | Path,
    jump_exist_file: bool = True,
) -> str:
    """Backward-compatible wrapper; the historical function returns WAV."""
    return convert_media_to_wave(source_mp4_file, target_folder)
