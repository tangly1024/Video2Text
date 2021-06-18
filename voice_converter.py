"""
音频转码
"""
from pydub import AudioSegment


def convert_media_to_wave(file_path):
    """
    统一将mp3,mp4转化为wav格式
    :param file_path:
    :return:
    """
    if file_path is None or len(str(file_path)) == 0:
        raise BaseException('输入文件地址为空')
    elif '.mp4' in file_path.lower():
        return mp3_2_wav(mp4_2_mp3(file_path))
    elif '.mp3' in file_path.lower():
        return mp3_2_wav(file_path)
    elif '.wav' in file_path.lower():
        return file_path
    else:
        raise BaseException('未知文件格式')


def mp3_2_wav(mp3_path):
    """
    这是MP3文件转化成WAV文件的函数
    :param mp3_path: MP3文件的地址
    :param wav_path: WAV文件的地址
    """
    mp3_file = AudioSegment.from_mp3(file=mp3_path)
    wav_path = mp3_path.replace('mp3', 'wav')
    mp3_file.export(wav_path, format="wav")
    return wav_path


# MP3_2_WAV


# 将mp4文件转为mp3音频文件,生成路径仍在原路径中(需要先下载moviepy库)
def mp4_2_mp3(path):
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        video = VideoFileClip(path)
        audio = video.audio
        new_path = path.replace('mp4', 'mp3')
        audio.write_audiofile(new_path)
        return new_path
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    video_path = r'/Users/tangly/Documents/文案音频素材/100w本金，怎么挣？.mp4'
    mp4_2_mp3(video_path)