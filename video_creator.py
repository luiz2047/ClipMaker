import glob
import json
import os
from pathlib import Path
from moviepy.video.fx.all import crop
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

    def load_parsed_data(self, output_file):
        with open(output_file, encoding="UTF-8") as f:
            self.parsed_data = parse_file(f.read())

    def load_transcribe_data(self, transcribe_file):
        with open(transcribe_file) as f:
            self.transcribe_data = json.load(f)["segments"]

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

        if (end_moment_timestamp - start_moment_timestamp) > 30:
            filtered_segments = self.filter_json_by_time(self.transcribe_data, start_moment_timestamp,
                                                         end_moment_timestamp)
            prev_end = start_moment_timestamp
            for segment in filtered_segments:
                segment_start = float(segment["start"])
                segment_end = float(segment["end"])

                # Adjust the start time if it exceeds the video duration
                segment_start = max(segment_start, prev_end)

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

        video_file = self.find_video_file(folder_path)
        self.movie_name = video_file

        i = 1
        for data in self.parsed_data:
            out_movie_name = Path(f"part_{i}")
            subs = self.create_subs_for_moment(data)
            if not subs:
                continue
            video = editor.VideoFileClip(video_file)
            (w, h) = video.size
            cropped_clip = crop(video, width=600, height=5000, x_center=w / 2, y_center=h / 2)
            annotated_clips = [self.annotate(cropped_clip.subclip(from_t, to_t), txt) for (from_t, to_t), txt in subs]
            final_clip = editor.concatenate_videoclips(annotated_clips)
            final_clip.write_videofile(self.results_dir / (str(out_movie_name) + ".mp4"), codec='mpeg4')
            with open(self.results_dir / (str(out_movie_name) + ".txt"), "w", encoding="utf-8") as f:
                text = "{}{}\n{}".format(data["title"], f"Part {i}", "\n".join(data["hashtags"]))
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
    movie_folder = Path("data/9rIy0xY99a0/")
    video_processor = VideoProcessor(movie_folder)
    video_processor.process_single_movie(movie_folder)
