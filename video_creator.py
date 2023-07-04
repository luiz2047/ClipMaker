import json
import os
from pathlib import Path
from moviepy.video.fx.all import crop
from output_parser import parse_file
from moviepy import editor


def annotate(clip, txt, txt_color='white', stroke_color="black", stroke_width=1.5, fontsize=40,
             font='ProximaNova-ExtraBold'):
    if txt is None or txt == '':
        return clip
    else:
        txt = separate_text(txt, max_line_length=25)
        txtclip = editor.TextClip(txt, fontsize=fontsize, stroke_color=stroke_color, stroke_width=stroke_width,
                                  font=font, color=txt_color)
        cvc = editor.CompositeVideoClip([clip, txtclip.set_pos(('center', 0.75), relative=True)])
        return cvc.set_duration(clip.duration)


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


def time_to_seconds(time_str):
    try:
        minutes, seconds = map(int, time_str.split(':'))
        total_seconds = minutes * 60 + seconds
        return float(total_seconds)
    except ValueError:
        raise ValueError("Invalid time format. Please provide time in 'm:s' format.")


def filter_json_by_time(json_data, window_start, window_end):
    result = []
    for item in json_data:
        start_time = item["start"]
        end_time = item["end"]
        if window_start <= start_time <= window_end or window_start <= end_time <= window_end:
            result.append(item)
    return result


def create_subs_for_moment(moment_data, segments):
    subs = []
    start_moment_timestamp = time_to_seconds(moment_data["start_timestamp"])
    end_moment_timestamp = time_to_seconds(moment_data["end_timestamp"]) + 10

    if (end_moment_timestamp - start_moment_timestamp) > 30:
        filtered_segments = filter_json_by_time(segments, start_moment_timestamp, end_moment_timestamp)
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
            subs.append(((prev_end, end_moment_timestamp), None))  # Add an empty subtitle to cover the remaining part

    return subs


if __name__ == "__main__":
    movie_fol = "data/4I5Q3UXkGd0/"
    movie_name = "4I5Q3UXkGd0.mp4"
    results_dir = Path(movie_fol, "results")
    results_dir.mkdir(parents=True, exist_ok=True)
    with open("data/4I5Q3UXkGd0/output.txt", encoding="UTF-8") as f:
        parsed_data = parse_file(f.read())
    print(parsed_data)
    with open("data/4I5Q3UXkGd0/transcribe.json") as f:
        transcribe = json.load(f)["segments"]
    i = 1
    for data in parsed_data:
        out_movie_name = Path(f"part_{i}")
        subs = create_subs_for_moment(data, transcribe)
        if not subs:
            continue
        video = editor.VideoFileClip(movie_fol + movie_name)
        (w, h) = video.size
        cropped_clip = crop(video, width=600, height=5000, x_center=w / 2, y_center=h / 2)
        annotated_clips = [annotate(cropped_clip.subclip(from_t, to_t), txt) for (from_t, to_t), txt in subs]
        final_clip = editor.concatenate_videoclips(annotated_clips)
        final_clip.write_videofile(os.path.join(results_dir, str(out_movie_name) + ".mp4"), codec='mpeg4')
        with open(os.path.join(results_dir, str(out_movie_name) + ".txt"), "w", encoding="utf-8") as f:
            text = "{}{}\n{}".format(data["title"], f"Part {i}",
                                     "\n".join(data["hashtags"]))
            f.write(text)
        i += 1
