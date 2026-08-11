"""Command-line interface for Video2Text."""

import argparse
from collections.abc import Sequence

from . import convert_to_text


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("必须大于 0")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="将本地音视频转为 UTF-8 文本")
    parser.add_argument("input", help="音频或视频文件路径")
    parser.add_argument("-o", "--output", default="output", help="输出根目录")
    parser.add_argument("--language", default="zh-CN", help="识别语言，默认 zh-CN")
    parser.add_argument(
        "--segment-length", type=positive_int, default=30, help="分段秒数，默认 30"
    )
    parser.add_argument("--workers", type=positive_int, default=5, help="并发数，默认 5")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = convert_to_text(
            args.input,
            args.output,
            language=args.language,
            segment_length=args.segment_length,
            workers=args.workers,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        parser.error(str(error))
    print(result)
    return 0
