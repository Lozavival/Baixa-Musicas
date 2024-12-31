import os

import eyed3
import moviepy.editor as mp
from pytubefix import YouTube
import ffmpeg

class YTDownload(YouTube):
    def download_audio(self, filename: str, overwrite: bool = False) -> str:
        path, name = os.path.split(filename)
        name = name.replace(".mp3", ".mp4")
        return self.streams.filter(mime_type="audio/mp4").order_by("abr").last().download(output_path=path, filename=name, skip_existing=not overwrite)
    
    def get_all_resolutions(self) -> list[str]:
        resolutions = []
        for stream in self.streams.filter(mime_type="video/mp4").order_by("resolution").desc():
            if stream.resolution not in resolutions:
                resolutions.append(stream.resolution)
        return resolutions
    
    def download_video(self, filename: str, res: str, overwrite: bool = False) -> None:
        # TODO: clear temporary files even if download fails
        path = os.path.dirname(filename)

        # Download video and audio streams separately
        video_stream = self.streams.filter(mime_type="video/mp4", resolution=res).last()
        audio_stream = self.streams.filter(mime_type="audio/mp4").order_by("abr").last()
        videopath = video_stream.download(path, filename="video.mp4")
        audiopath = audio_stream.download(path, filename="audio.mp4")

        # Join video and audio streams
        video = ffmpeg.input(videopath)
        audio = ffmpeg.input(audiopath)
        ffmpeg.output(video, audio, filename).run(overwrite_output=overwrite)

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
