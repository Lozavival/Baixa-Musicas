import os

import eyed3
import ffmpeg
import moviepy.editor as mp
from pytubefix import YouTube


class YTDownload(YouTube):
    """
    A class that extends YouTube to provide additional functionality for
    downloading audio and video from YouTube.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(client="ANDROID", *args, **kwargs)

    def download_audio(self, filename: str, overwrite: bool = False) -> str:
        """
        Download the audio from the YouTube video.

        Parameters
        ----------
        filename : str
            The path to the output file.
        overwrite : bool, optional
            Whether to overwrite the file if it already exists. Defaults to False.

        Returns
        -------
        str: The path to the downloaded file.
        """
        path, name = os.path.split(filename)
        name = name.replace(".mp3", ".mp4")
        return (
            self.streams.filter(mime_type="audio/mp4")
            .order_by("abr")
            .last()
            .download(output_path=path, filename=name, skip_existing=not overwrite)
        )

    def get_all_resolutions(self) -> list[str]:
        """
        Get a list of all the available resolutions for the video.

        Parameters
        ----------
        ---

        Returns
        -------
        list[str]: A list of the available resolutions.
        """
        resolutions = []
        for stream in self.streams.filter(mime_type="video/mp4"):
            if stream.resolution not in resolutions:
                resolutions.append(stream.resolution)
        return sorted(resolutions, reverse=True)

    def download_video(self, filename: str, res: str, overwrite: bool = False) -> None:
        """
        Download the video from the YouTube video.

        Parameters
        ----------
        filename : str
            The path to the output file.
        res : str
            The resolution of the video to download.
        overwrite : bool, optional
            Whether to overwrite the file if it already exists. Defaults to False.

        Returns
        -------
        None
        """
        # Download video and audio streams separately
        video_stream = self.streams.filter(mime_type="video/mp4", resolution=res).last()
        audio_stream = self.streams.filter(mime_type="audio/mp4").order_by("abr").last()
        videopath = video_stream.download(filename="video.mp4")
        audiopath = audio_stream.download(filename="audio.mp4")

        try:
            # Join video and audio streams
            video = ffmpeg.input(videopath)
            audio = ffmpeg.input(audiopath)
            ffmpeg.output(video, audio, filename).run(overwrite_output=overwrite)
        finally:
            # Delete temporary files
            os.remove(videopath)
            os.remove(audiopath)

    def convert_to_mp3(self, mp4_path: str) -> bool:
        """
        Convert the video file to an mp3 file.

        Parameters
        ----------
        mp4_path : str
            The path to the mp4 file.

        Returns
        -------
        bool: Whether the conversion was successful.
        """
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
