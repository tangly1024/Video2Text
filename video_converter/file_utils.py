import os

from video_converter.log_utils import get_logger

log = get_logger('file_utils')


def get_file_name_and_extension(file_path):
    """
    返回元祖 (file_name,file_extions)
    :param file_path:
    :return:
    """
    log.info('获取文件名和扩展 %s' % file_path)
    (filepath, temp_filename) = os.path.split(file_path)
    return os.path.splitext(temp_filename)


def combine_text(from_text_array, target_text_file):
    """
    合并一组文本文件
    :param target_text_file:  目标文件名
    :param from_text_array: 源文本文件数组
    :return:
    """
    log.info('开始合并文件, 数量： %s' % len(from_text_array))
    with open(target_text_file, 'a+') as k:
        k.seek(0)
        k.truncate()  # 从第0行开始清空文件
        for text_file in from_text_array:
            log.debug('合并 %s' % text_file)
            if os.path.exists(text_file):
                with open(text_file) as f:
                    k.write(f.read() + "\r\n")
            else:
                break
    log.info('文件合并完成, 目标文件名： %s' % target_text_file)
