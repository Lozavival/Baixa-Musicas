import os

import eyed3
import moviepy.editor as mp
from pytubefix import YouTube
import ffmpeg

class YTDownload(YouTube):
    def download_audio(self, path: str) -> str:
        return self.streams.filter(mime_type="audio/mp4").order_by("abr").last().download(path)
    
    def get_all_resolutions(self) -> list[str]:
        return [stream.resolution for stream in self.streams.filter(mime_type="video/mp4").order_by("resolution").desc()]
    
    def download_video(self, path: str, res: str) -> None:
        # Download video and audio streams separately
        video_stream = self.streams.filter(mime_type="video/mp4", resolution=res).last()
        audio_stream = self.streams.filter(mime_type="audio/mp4").order_by("abr").last()
        videopath = video_stream.download(path, filename="video.mp4")
        audiopath = audio_stream.download(path, filename="audio.mp4")

        # Join video and audio streams
        video = ffmpeg.input(videopath)
        audio = ffmpeg.input(audiopath)
        ffmpeg.output(video, audio, os.path.join(path, self.title + ".mp4")).run()

        # Delete temporary files
        os.remove(videopath)
        os.remove(audiopath)

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
