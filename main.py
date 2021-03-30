"""
程序主入口
"""
import datetime
import os
import threading
import time
import wave
import traceback
import logging
import speech_recognition as sr
from pydub import AudioSegment

from voice_converter import handle_voice_converter

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


def split_file(voice_file, project_name):
    """
    根据音频文件时长分割
    :param voice_file:
    :return: file_array[]
    """
    # 获取音频时长
    f = wave.open(voice_file, "rb")
    time_length = int(f.getparams()[3] / f.getparams()[2])
    print('音频文件时长 %s' % time_length)

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
        out_put_file_path = split_folder_path + '%s-%d.wav' % (project_name, i + 1)
        read_audio[i * 30 * 1000:((i + 1) * 30 + 2) * 1000].export(out_put_file_path, format="wav")
        res.append(out_put_file_path)
    return res


def convert_by_google(voice_file, dst_file_name, semaphore, finished_text_array):
    try:
        semaphore.acquire()
        r = sr.Recognizer()
        with sr.WavFile(voice_file) as source:
            print("%s 开始转换" % voice_file)
            audio = r.record(source)
            # text = r.recognize_ibm(audio, username='IBM_USERNAME', password='IBM_PASSWORD', language='zh-CN')
            text = r.recognize_google(audio, language='zh-CN')
            open(dst_file_name, 'a+').write(text)
            finished_text_array.append(dst_file_name)
            time.sleep(1)
            temp_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('完成 %s %s' % (temp_time, dst_file_name))
    except Exception as e:
        temp_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.error('失败 %s %s' % (temp_time, dst_file_name), e)
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
    semaphore = threading.BoundedSemaphore(5)
    return_text_array = []
    for voice_file in file_array:
        dest_file_path = voice_file.replace('.wav', '.txt')
        t = threading.Thread(target=convert_by_google, args=(voice_file, dest_file_path, semaphore, return_text_array,),
                             name=voice_file)
        threads.append(t)
        t.start()
        time.sleep(1)
        # 等待所有线程任务结束。
    for t in threads:
        t.join()
    end_time = datetime.datetime.now()
    last = end_time - start_time
    print('总共花费时间：%s' % last)
    return return_text_array


def combine_text(text_array, dest_text_file):
    """
    将一组文本文件合并到一个文本中
    :param text_array:
    :return:
    """
    with open(dest_text_file, 'a+') as k:
        k.seek(0)
        k.truncate()  # 从第0行开始清空文件
        for text_file in text_array:
            if os.path.exists(text_file):
                with open(text_file) as f:
                    k.write(f.read() + "\r\n")
                    print('合并', text_file)
            else:
                break


if __name__ == '__main__':
    try:
        voice_path = r'YourVoiceOrVideoPathHere'

        # 按照目标文件名创建文件夹
        project_name = get_file_name(voice_path)[0]

        project_path = r'./output/' + project_name
        if not os.path.exists(project_path):
            os.makedirs(project_path)

        # 统一预处理文件格式 转Wav
        voice_path = handle_voice_converter(voice_path)
        #
        # 根据音频时长分割，过长影响效率
        split_file_array = split_file(voice_path, project_name)
        #
        # 音频转文字
        text_array = convert_2_text(split_file_array)

        # 将文本统一合并到一个文件夹中
        combine_text(text_array, project_path + '/' + project_name + '.txt')
    except Exception as e:
        logging.error(traceback.format_exc())
