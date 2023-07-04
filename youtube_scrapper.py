import json
import os
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube
from tqdm import tqdm
from pytube import Channel

save_folder = Path("data")


def download_video(link, save_path):
    yt = YouTube(link)
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    video.download(save_path, filename=link.split("=")[-1] + ".mp4")
    save_metadata(yt, save_path)


def convert_to_mp3(mp4_file, mp3_file):
    video = VideoFileClip(mp4_file)
    audio = video.audio
    audio.write_audiofile(mp3_file)
    audio.close()
    video.close()


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


if __name__ == "__main__":
    # with open(link_files) as file:
    #     links = file.read().splitlines()
    c = Channel('https://www.youtube.com/@Vsauce')

    for link in tqdm(c.video_urls[:100]):
        try:
            save_path = Path(save_folder, link.split("=")[-1])
            save_path.mkdir(parents=True, exist_ok=False)
            mp4_file = Path(save_path, link.split("=")[-1] + ".mp4")
            mp3_file = Path(save_path, link.split("=")[-1] + ".mp3")
            download_video(link, save_path)
            convert_to_mp3(str(mp4_file), str(mp3_file))
        except:
            continue

