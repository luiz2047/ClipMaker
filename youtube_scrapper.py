import json
import os
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube
from tqdm import tqdm
from pytube import Channel


class YouTubeDownloader:
    def __init__(self, save_folder):
        self.save_folder = save_folder

    def download_video(self, link, save_path):
        yt = YouTube(link)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        video.download(save_path, filename=link.split("=")[-1] + ".mp4")
        self.save_metadata(yt, save_path)

    @staticmethod
    def convert_to_mp3(mp4_file, mp3_file):
        video = VideoFileClip(mp4_file)
        audio = video.audio
        audio.write_audiofile(mp3_file)
        audio.close()
        video.close()

    @staticmethod
    def save_metadata(yt, save_path):
        metadata = {
            "title": yt.title,
            "description": yt.description,
            "length": yt.length,
            "views": yt.views,
            "author": yt.author,
            "rating": yt.rating,
            "url": yt.watch_url
        }
        with open(os.path.join(save_path, "metadata.json"), 'w') as fp:
            json.dump(metadata, fp)

    def download_channel_videos(self, channel_url, num_videos=100):
        c = Channel(channel_url)
        for link in tqdm(c.video_urls[:num_videos]):
            try:
                save_path = Path(self.save_folder, link.split("=")[-1])
                save_path.mkdir(parents=True, exist_ok=False)
                mp4_file = Path(save_path, link.split("=")[-1] + ".mp4")
                mp3_file = Path(save_path, link.split("=")[-1] + ".mp3")
                self.download_video(link, save_path)
                self.convert_to_mp3(str(mp4_file), str(mp3_file))
            except:
                continue


if __name__ == "__main__":
    save_folder = Path("data")
    downloader = YouTubeDownloader(save_folder)
    downloader.download_channel_videos('https://www.youtube.com/@Vsauce', num_videos=100)
