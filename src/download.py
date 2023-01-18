import os
import moviepy.editor as mp
from pytube import YouTube


def download(link: str, path: str) -> str:
    return YouTube(link).streams.filter(only_audio=True).first().download(path)


def convert_to_map3(mp4_path: str) -> bool:
    mp3_path = mp4_path.replace(".mp4", ".mp3")
    new_file = mp.AudioFileClip(mp4_path)
    new_file.write_audiofile(mp3_path)
    os.remove(mp4_path)
    return True
