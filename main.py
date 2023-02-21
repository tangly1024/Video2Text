"""
程序主入口
"""
from video_converter import convert_to_text

if __name__ == '__main__':
    # 输入目标文件路径 for_example: r'/Users/xx/xxx.mp4'
    source_media_path = r'[your_media_file_path]'
    convert_to_text(source_media_path=source_media_path)
