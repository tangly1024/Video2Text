"""
程序主入口
"""
import datetime
import os
import threading
import wave
import traceback
import logging
import speech_recognition as sr
from pydub import AudioSegment

from voice_converter import convert_media_to_wave

logging.basicConfig(filename='log.log',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)


def get_file_name(file_path):
    """
    返回元祖 (file_name,file_extions)
    :param file_path:
    :return:
    """
    (filepath, temp_filename) = os.path.split(file_path)
    return os.path.splitext(temp_filename)


def get_audio_duration(voice_file):
    """
    获取音频时长
    :param voice_file:
    :return:
    """
    # 获取音频时长
    f = wave.open(voice_file, "rb")
    return int(f.getparams()[3] / f.getparams()[2])


def split_file(voice_file, file_name_prefix):
    """
    根据音频文件时长分割
    :param file_name_prefix:
    :param voice_file:
    :return: file_array[]
    """
    time_length = get_audio_duration(voice_file)
    # 音频分割输出
    read_audio = AudioSegment.from_wav(voice_file)
    # 创建分割输出文件夹
    split_folder_path = r'%s/split/' % project_path
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
    return res


def convert_by_google(voice_file, dst_file_name, semaphore, r):
    try:
        semaphore.acquire()
        with sr.WavFile(voice_file) as source:
            print("开始转换 %s ；目标位置 %s" % (voice_file, dst_file_name))
            # 如果目标文件已经存在就不重新创建
            audio = r.record(source)
            # text = r.recognize_ibm(audio, username='IBM_USERNAME', password='IBM_PASSWORD', language='zh-CN')
            text = r.recognize_google(audio, language='zh-CN')
            open(dst_file_name, 'a+').write(text)
            temp_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('转换完成 %s %s' % (temp_time, dst_file_name))
    except:
        temp_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.error('失败 %s %s' % (temp_time, dst_file_name))
    finally:
        semaphore.release()


def convert_2_text(file_array):
    """
    调用音频api将媒体转为文字
    :param file_array: 分割后的音频文件路径
    :return: text_path_array[]
    """
    # 获取文件夹下的音频文件名
    start_time = datetime.datetime.now()
    threads = []
    # 信号量 控制API并发请求数为5
    semaphore = threading.BoundedSemaphore(5)
    return_text_array = []
    r = sr.Recognizer()
    for voice_file in file_array:
        dest_file_path = voice_file.replace('.wav', '.txt')
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
    print('总共花费时间：%s' % last)
    return return_text_array


def combine_text(from_text_array, target_text_file):
    """
    将一组文本文件合并到一个文本中
    :param target_text_file:  目标文本文件
    :param from_text_array: 来源文本文件数组
    :return:
    """
    logging.info('开始合并文件, 数量： %s' % len(from_text_array))
    with open(target_text_file, 'a+') as k:
        k.seek(0)
        k.truncate()  # 从第0行开始清空文件
        for text_file in from_text_array:
            if os.path.exists(text_file):
                with open(text_file) as f:
                    k.write(f.read() + "\r\n")
                    print('合并', text_file)
            else:
                break


if __name__ == '__main__':
    try:
        media_path = r'/Users/tangly/Documents/【产品】/文章素材/男女大脑不同.mp4'

        # 获取文件名作为项目名
        project_name = get_file_name(media_path)[0]

        project_path = r'./output/' + project_name
        if not os.path.exists(project_path):
            os.makedirs(project_path)

        # 统一预处理文件格式 转Wav
        voice_path = convert_media_to_wave(media_path)

        # 根据音频时长分割，过长影响效率
        split_file_array = split_file(voice_path, project_name)

        # 音频转文字
        text_array = convert_2_text(split_file_array)

        # 将文本统一合并到一个文件夹中
        combine_text(text_array, project_path + '/' + project_name + '.txt')
    except Exception as e:
        logging.error(traceback.format_exc())
