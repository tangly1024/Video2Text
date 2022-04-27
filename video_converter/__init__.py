from video_converter.voice_utils import convert_media_to_wave, split_voice_file, convert_audios_to_text
from video_converter.log_utils import get_logger


import os
import traceback

from . import convert_media_to_wave, split_voice_file, convert_audios_to_text, get_logger
from .file_utils import get_file_name_and_extension, combine_text
log = get_logger('file_utils')


def convert_to_text(source_media_path, output_path='./output'):
    """
    将指定的音频或视频文件转换为文本
    :param source_media_path: 源文件路径
    :param output_path: 输出目录
    :return:
    """
    try:
        if os.path.exists(source_media_path) != True:
            raise BaseException('输入文件不存在')

        # 获取文件名作为项目名
        project_name = get_file_name_and_extension(source_media_path)[0]

        # 创建输出文件夹
        output_path = r'./output/' + project_name + '/'
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # 统一预处理文件 转Wav
        voice_path = convert_media_to_wave(source_media_path, target_folder=output_path)

        # 根据音频时长分割，过长的文件无法转换
        split_file_array = split_voice_file(voice_path, project_name, output_path)

        # 批量音频转文字
        text_array = convert_audios_to_text(split_file_array)

        # 将文本文件组，合并成一个文档
        combine_text(text_array, output_path + '/' + project_name + '.txt')
    except Exception as e:
        log.error('视频转文字失败',traceback.format_exc())
