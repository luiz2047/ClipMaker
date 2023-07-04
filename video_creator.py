import glob
import json
import os
from pathlib import Path
from moviepy.video.fx.all import crop
from moviepy.video.io.VideoFileClip import VideoFileClip

from output_parser import parse_file
from moviepy import editor


class VideoProcessor:
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.movie_folder = ""
        self.movie_name = ""
        self.transcribe_data = []
        self.parsed_data = []
        self.results_dir = None
        self.movie_duration = None
        self.metadata = None

    def load_parsed_data(self, output_file):
        with open(output_file, encoding="UTF-8") as f:
            self.parsed_data = parse_file(f.read())

    def load_transcribe_data(self, transcribe_file):
        with open(transcribe_file) as f:
            self.transcribe_data = json.load(f)["segments"]

    def load_video_metadata(self, metadata_file):
        with open(metadata_file) as f:
            self.metadata = json.load(f)

    @staticmethod
    def separate_text(text, max_line_length=30):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= max_line_length:  # +1 for the space between words
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return "\n".join(lines)

    @staticmethod
    def time_to_seconds(time_str):
        try:
            minutes, seconds = map(int, time_str.split(':'))
            total_seconds = minutes * 60 + seconds
            return float(total_seconds)
        except ValueError:
            raise ValueError("Invalid time format. Please provide time in 'm:s' format.")

    @staticmethod
    def filter_json_by_time(json_data, window_start, window_end):
        result = []
        for item in json_data:
            start_time = item["start"]
            end_time = item["end"]
            if window_start <= start_time <= window_end or window_start <= end_time <= window_end:
                result.append(item)
        return result

    def create_subs_for_moment(self, moment_data):
        subs = []
        start_moment_timestamp = self.time_to_seconds(moment_data["start_timestamp"])
        end_moment_timestamp = self.time_to_seconds(moment_data["end_timestamp"]) + 10
        end_moment_timestamp = min(self.movie_duration, end_moment_timestamp)
        if (end_moment_timestamp - start_moment_timestamp) > 30:

            filtered_segments = self.filter_json_by_time(self.transcribe_data, start_moment_timestamp,
                                                         end_moment_timestamp)
            prev_end = start_moment_timestamp
            for segment in filtered_segments:
                segment_start = int(segment["start"])
                segment_end = int(segment["end"])

                if segment_start > prev_end:
                    subs.append(((prev_end, segment_start), None))  # Add an empty subtitle to cover the gap

                subs.append(((segment_start, segment_end), segment["text"]))
                prev_end = segment_end

            if prev_end < end_moment_timestamp:
                subs.append(
                    ((prev_end, end_moment_timestamp), None))  # Add an empty subtitle to cover the remaining part

        return subs

    def annotate(self, clip, txt, txt_color='white', stroke_color="black", stroke_width=1.5, fontsize=40,
                 font='ProximaNova-ExtraBold'):
        if txt is None or txt == '':
            return clip
        else:
            txt = self.separate_text(txt, max_line_length=25)
            txtclip = editor.TextClip(txt, fontsize=fontsize, stroke_color=stroke_color, stroke_width=stroke_width,
                                      font=font, color=txt_color)
            cvc = editor.CompositeVideoClip([clip, txtclip.set_pos(('center', 0.75), relative=True)])
            return cvc.set_duration(clip.duration)

    def process_whole_folder(self):
        data_folder = Path(self.movie_folder)
        for folder in data_folder.iterdir():
            if folder.is_dir():
                try:
                    self.process_single_movie(folder)
                except Exception as ex:
                    print(f"ERROR Troubles with dir: {folder}\n{ex}")

    def process_single_movie(self, folder_path):
        self.results_dir = folder_path / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.load_parsed_data(folder_path / "output.txt")
        self.load_transcribe_data(folder_path / "transcribe.json")
        self.load_video_metadata(folder_path / "metadata.json")
        video_file = self.find_video_file(folder_path)
        self.movie_name = video_file
        # print(self.parsed_data)
        i = 1
        for data in self.parsed_data:
            out_movie_name = Path(f"part_{i}")
            video = editor.VideoFileClip(video_file)
            self.movie_duration = video.duration
            subs = self.create_subs_for_moment(data)
            if not subs:
                continue
            (w, h) = video.size
            cropped_clip = crop(video, width=600, height=5000, x_center=w / 2, y_center=h / 2)
            # print(subs)
            annotated_clips = [self.annotate(cropped_clip.subclip(from_t, to_t), txt) for (from_t, to_t), txt in subs]
            final_clip = editor.concatenate_videoclips(annotated_clips)
            final_clip.write_videofile(str(self.results_dir / out_movie_name) + ".mp4", codec='mpeg4')
            with open(str(self.results_dir / out_movie_name) + ".txt", "w", encoding="utf-8") as f:
                text = "{} {}\n{}\n{}".format(self.metadata["title"],
                                            f"Part {i}",
                                            data["title"],
                                            "\n".join(data["hashtags"]))
                f.write(text)
            i += 1

    @staticmethod
    def find_video_file(folder_path):
        video_files = list(glob.glob(f"{folder_path}/*.mp4"))
        if len(video_files) == 1:
            return video_files[0]
        else:
            raise ValueError("Could not find a valid video file in the folder.")


if __name__ == "__main__":
    movie_folder = Path("data/ACUuFg9Y9dY/")
    video_processor = VideoProcessor(movie_folder)
    video_processor.process_single_movie(movie_folder)
