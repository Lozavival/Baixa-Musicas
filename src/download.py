import os

import eyed3
import moviepy.editor as mp
from pytube import YouTube


class YTDownload(YouTube):
    def download_stream(self, path: str) -> str:
        return self.streams.filter(only_audio=True).first().download(path)

    def convert_to_mp3(self, mp4_path: str) -> bool:
        # convert mp4 file to mp3 file
        mp3_path = mp4_path.replace(".mp4", ".mp3")
        with mp.AudioFileClip(mp4_path) as audio:
            audio.write_audiofile(mp3_path)
        os.remove(mp4_path)

        # add metadata to mp3 file
        mp3_file = eyed3.load(mp3_path)
        mp3_file.tag.artist = self.author
        mp3_file.tag.save()
        return True
