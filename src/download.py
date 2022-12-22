import os

import moviepy.editor as mp
from pytube import YouTube


def remove_unsupported_characters(string: str) -> str:
    unsupported = '\\/:*?"<>|~#%&+,.}{$!`=[]'
    return string.translate({ord(i): None for i in unsupported})


def download(link: str, path: str) -> str:
    yt = YouTube(link)
    yt.streams.filter(only_audio=True).first().download(path)
    return yt.title


def convert_to_mp3(path: str, title: str) -> bool:
    for file in os.listdir(path):
        if remove_unsupported_characters(title) + '.mp4' == file:
            mp4_path = os.path.join(path, file)
            mp3_path = os.path.join(path, os.path.splitext(file)[0]+'.mp3')
            new_file = mp.AudioFileClip(mp4_path)
            new_file.write_audiofile(mp3_path)
            os.remove(mp4_path)
            return True
    return False
