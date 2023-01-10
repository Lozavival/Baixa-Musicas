from pytube import YouTube


def download(link: str, path: str) -> None:
    YouTube(link).streams.filter(only_audio=True).first().download(path)
    
