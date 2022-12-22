from pytube import YouTube
import moviepy.editor as mp
import os


def remove_unsupported_characters(string: str) -> str:
    return string.replace(",", "")


def download(link: str, path: str) -> None:
    yt = YouTube(link)
    yt.streams.filter(only_audio=True).first().download(path)
    
    for file in os.listdir(path):
        if remove_unsupported_characters(yt.title) + '.mp4' == file:
            mp4_path = os.path.join(path, file)
            mp3_path = os.path.join(path, os.path.splitext(file)[0]+'.mp3')
            new_file = mp.AudioFileClip(mp4_path)
            new_file.write_audiofile(mp3_path)
            os.remove(mp4_path)


if __name__ == "__main__":
    download(input(), os.getcwd())
