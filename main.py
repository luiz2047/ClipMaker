import argparse
import os
from pathlib import Path
from youtube_scrapper import YouTubeDownloader
from subtitle_creator import TranscriptionProcessor
from moments_creating_gpt import GptProcessor
from video_creator import VideoProcessor
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


def main(args):
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "full":
        logger.info("Start full pipeline")
        logger.info("Start YouTubeDownloader")
        downloader = YouTubeDownloader(data_dir)
        downloader.download_channel_videos(args.channel_link)
        logger.info("End YouTubeDownloader")
        logger.info("Start Whisper")
        transcription_processor = TranscriptionProcessor(model_name=args.whisper_model, device=args.cuda)
        transcription_processor.transcribe_audio_files(data_dir)
        logger.info("End Whisper")
        logger.info("Start ChatGPT ideas creating")
        gpt_processor = GptProcessor(model_name='gpt-3.5-turbo')
        gpt_processor.process_data_folder(data_dir)
        logger.info("End ChatGPT ideas creating")
        logger.info("Start VideoProcessor")
        video_processor = VideoProcessor(data_dir)
        video_processor.process_whole_folder()
        logger.info("End VideoProcessor")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Full Pipeline to create tiktok videos')
    parser.add_argument('-d', '--data_dir', type=str, default='data', help='Path to data directory')
    parser.add_argument('-l', '--channel_link', type=str, default='https://www.youtube.com/@Vsauce',
                        help='YouTube link of channel')
    parser.add_argument('-n', '--num_video', type=int, default=10,
                        help='Number videos')
    parser.add_argument('-m', '--mode', type=str, default="full",
                        help='Pipeline mode')
    parser.add_argument('--whisper_model', type=str, default='small',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper model to transcribe')
    parser.add_argument('--cuda', type=str, default='cuda',
                        help='Cuda')
    parser.add_argument('--gpt_model', type=str, default='gpt-3.5-turbo',
                        help='GPT OpenAI model to generate titles, hashtags, description, timestamps')
    args = parser.parse_args()
