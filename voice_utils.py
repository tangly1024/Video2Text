"""
音频转码
"""
import os
from shutil import copyfile

from pydub import AudioSegment
import speech_recognition as sr
import datetime
import threading

import wave
import logging

from file_utils import get_file_name_and_extension

logger = logging.getLogger()

logging.basicConfig(filename='log.log',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
logging.getLogger().addHandler(console)


def split_voice_file(voice_file, file_name_prefix, output_path='./', split_length=30):
    """
    根据音频文件时长分割
    :param file_name_prefix:
    :param voice_file:
    :param split_length: 每段音频时长默认30秒
    :return: file_array[]
    """
    time_length = get_audio_duration(voice_file)
    # 音频分割输出
    read_audio = AudioSegment.from_wav(voice_file)
    # 创建分割输出文件夹
    split_folder_path = r'%s/split/' % output_path
    if not os.path.exists(split_folder_path):
        os.makedirs(split_folder_path)

    # 每段音频30s
    kn = int(time_length / 30) + 1
    res = []
    for i in range(kn):
        suffix = (str(i + 1)).zfill(2)
        out_put_file_path = split_folder_path + '%s-%s.wav' % (file_name_prefix, suffix)
        read_audio[i * 30 * 1000:((i + 1) * 30 + 2) * 1000].export(out_put_file_path, format="wav")
        res.append(out_put_file_path)
    logging.debug('源文件分割为[%s]个时长[%s]s的子文件' % (len(res), split_length))
    return res


def convert_audios_to_text(file_array, max_convert_thread=5, jump_exists_file=True):
    """
    将音频数组批量转文字
    :param max_convert_thread: 同时转换文件线程的上限
    :param file_array: 分割后的音频文件路径
    :param jump_exists_file: 是否跳过已存在的文件
    :return: text_path_array[] 返回转换好的文本文件数组
    """
    # 获取文件夹下的音频文件名
    start_time = datetime.datetime.now()
    threads = []
    # 信号量 控制API并发请求数
    semaphore = threading.BoundedSemaphore(max_convert_thread)
    return_text_array = []
    r = sr.Recognizer()

    logging.debug('启动[%s]个线程对音频文件进行批量转换' % max_convert_thread)
    for voice_file in file_array:
        dest_file_path = voice_file.replace('.wav', '.txt')
        if jump_exists_file & os.path.exists(dest_file_path):
            logging.debug('跳过已存在文件,跳过转换 %s' % dest_file_path)
            return_text_array.append(dest_file_path)
            continue
        t = threading.Thread(target=convert_by_google,
                             args=(voice_file, dest_file_path, semaphore, r,),
                             name=voice_file)
        return_text_array.append(dest_file_path)
        threads.append(t)
        t.start()

    # 等待所有线程任务结束。
    for t in threads:
        t.join()
    end_time = datetime.datetime.now()
    last = end_time - start_time
    logging.debug('音频转换总耗时：[%s]s' % last)
    return return_text_array


def convert_by_google(voice_file, dst_file_name, semaphore, r):
    """
    使用google的speech-to-text进行转换 https://cloud.google.com/speech-to-text?hl=zh-cn
    :param voice_file:
    :param dst_file_name:
    :param semaphore:
    :param r:
    :return:
    """
    try:
        semaphore.acquire()
        with sr.WavFile(voice_file) as source:
            logging.debug("正在转换 %s ；目标位置 %s" % (voice_file, dst_file_name))
            # 如果目标文件已经存在就不重新创建
            audio = r.record(source)
            # text = r.recognize_ibm(audio, username='IBM_USERNAME', password='IBM_PASSWORD', language='zh-CN')
            text = r.recognize_google(audio, language='zh-CN')
            open(dst_file_name, 'a+').write(text)
            temp_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.debug('转换完成 %s %s' % (temp_time, dst_file_name))
    except:
        temp_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.error('失败 %s %s' % (temp_time, dst_file_name))
    finally:
        semaphore.release()


def get_audio_duration(voice_file):
    """
    获取音频时长
    :param voice_file:
    :return:
    """
    # 获取音频时长
    f = wave.open(voice_file, "rb")
    duration = int(f.getparams()[3] / f.getparams()[2])
    logging.debug('源文件音频总时长 %s s' % duration)
    return duration


def convert_media_to_wave(source_file, target_folder):
    """
    统一将mp3,mp4转化为wav格式
    :param target_folder: 目标文件夹
    :param source_file:
    :return:
    """
    if source_file is None or len(str(source_file)) == 0:
        raise BaseException('输入文件地址为空')
    elif '.mp4' in source_file.lower():
        logging.debug('MP4转WAV')
        return mp3_2_wav(mp4_2_mp3(source_file, target_folder), target_folder)
    elif '.mp3' in source_file.lower():
        logging.debug('MP3转WAV')
        return mp3_2_wav(source_file, target_folder)
    elif '.wav' in source_file.lower():
        logging.debug('源文件格式为WAV，复制到输出目录下')
        (filepath, temp_filename) = os.path.split(source_file)
        taarget_file = target_folder + temp_filename
        copyfile(source_file, taarget_file)
        return taarget_file
    else:
        raise BaseException('未知文件格式')


def mp3_2_wav(source_mp3_file, target_folder, jump_exist_file=True):
    """
    这是MP3文件转化成WAV文件的函数
    :param jump_exist_file: 目标文件存在时跳过
    :param target_folder: 目标文件夹
    :param source_mp3_file: 源MP3文件的地址
    :param wav_path: WAV文件的地址
    """
    wav_path = target_folder + get_file_name_and_extension(source_mp3_file)[0] + '.wav'
    if jump_exist_file & os.path.exists(wav_path):
        return wav_path
    mp3_file = AudioSegment.from_mp3(file=source_mp3_file)
    mp3_file.export(wav_path, format="wav")
    return wav_path


# MP3_2_WAV


# 将mp4文件转为mp3音频文件,生成路径仍在原路径中(需要先下载moviepy库)
def mp4_2_mp3(source_mp4_file, target_folder, jump_exist_file=True):
    """
    MP4文件转MP3音频
    :param source_mp4_file: 源文件地址
    :param target_folder:  目标文件夹
    :param jump_exist_file: 文件已存在时跳过
    :return:
    """
    try:
        mp3_path = target_folder + get_file_name_and_extension(source_mp4_file)[0] + '.wav'
        if jump_exist_file & os.path.exists(mp3_path):
            return mp3_path
        from moviepy.video.io.VideoFileClip import VideoFileClip
        mp4_video = VideoFileClip(source_mp4_file)
        mp4_audio = mp4_video.audio
        mp4_audio.write_audiofile(mp3_path)
        return mp3_path
    except Exception as e:
        logging.debug(e)
        return None


if __name__ == '__main__':
    video_path = r'/Users/tangly/Documents/文案音频素材/100w本金，怎么挣？.mp4'
    mp4_2_mp3(video_path)
