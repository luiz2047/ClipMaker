import re
from datetime import datetime


def remove_tabulations_and_lists(text):
    text_without_multiple_enter = re.sub(r'\n+', '\n', text)
    text_without_lists = re.sub(r'\d+\.\s*', '', text_without_multiple_enter)
    text_without_tabs = text_without_lists.replace("\t", "")
    lines = text_without_tabs.split('\n')
    clean_lines = [line.strip() for line in lines]
    cleaned_text = '\n'.join(clean_lines)
    cleaned_text = cleaned_text.replace(" Timestamp:", "\nTimestamp:")
    cleaned_text = cleaned_text.replace(" -> ", "->")
    return cleaned_text


def parse_file(file_content):
    file_content = remove_tabulations_and_lists(file_content)
    pattern = r'(?:Title(?: of moment)?: )?(.*?)\nHashtags: (.*?)\nDescription: (.*?)\nTimestamp: ([0-9:]+)(->|-)([0-9:]+)'
    matches = re.findall(pattern, file_content, re.DOTALL)
    parsed_data = []

    for match in matches:
        title = match[0]
        hashtags = [tag.strip() for tag in match[1].split()]
        description = match[2]
        start_timestamp = match[3]
        end_timestamp = match[5]

        parsed_data.append({
            'title': title,
            'hashtags': hashtags,
            'description': description,
            'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp
        })

    return adjust_moments_timestamps(parsed_data)


def convert_timestamp_to_seconds(timestamp):
    parts = timestamp.split(':')
    minutes = float(parts[0])
    seconds = float(parts[1])
    return minutes * 60 + seconds

def convert_seconds_to_timestamp(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def adjust_moments_timestamps(moments):
    corrected_moments = []
    prev_end_timestamp = None

    for i in range(len(moments)):
        moment = moments[i]

        start_timestamp = convert_timestamp_to_seconds(moment['start_timestamp'])
        end_timestamp = convert_timestamp_to_seconds(moment['end_timestamp'])

        if prev_end_timestamp is not None and start_timestamp - prev_end_timestamp > 30:
            # If the gap between moments is too large, create a new moment using data from the previous one
            corrected_moments.append({
                'start_timestamp': convert_seconds_to_timestamp(prev_end_timestamp),
                'end_timestamp': convert_seconds_to_timestamp(start_timestamp),
            })

        corrected_moments.append(moment)
        prev_end_timestamp = end_timestamp

        if i < len(moments) - 1:
            next_start_timestamp = convert_timestamp_to_seconds(moments[i + 1]['start_timestamp'])

            if next_start_timestamp - end_timestamp > 30:
                # If there is a gap between moments, fill it with a new moment
                gap_duration = next_start_timestamp - end_timestamp

                if gap_duration <= 120:
                    # Fill the gap with a single moment
                    corrected_moments.append({
                        'start_timestamp': convert_seconds_to_timestamp(end_timestamp),
                        'end_timestamp': convert_seconds_to_timestamp(next_start_timestamp),
                    })
                else:
                    # Split the gap into multiple 2-minute moments
                    num_segments = int(gap_duration // 120)
                    segment_duration = gap_duration / num_segments

                    for j in range(num_segments):
                        segment_start = end_timestamp + j * segment_duration
                        segment_end = segment_start + segment_duration

                        corrected_moments.append({
                            'start_timestamp': convert_seconds_to_timestamp(segment_start),
                            'end_timestamp': convert_seconds_to_timestamp(segment_end),
                        })

    # Remove overlapping moments
    final_moments = []
    prev_end_timestamp = None
    for moment in corrected_moments:
        start_timestamp = convert_timestamp_to_seconds(moment['start_timestamp'])
        end_timestamp = convert_timestamp_to_seconds(moment['end_timestamp'])

        if prev_end_timestamp is not None and start_timestamp < prev_end_timestamp:
            # Skip overlapping moments
            continue

        final_moments.append(moment)
        prev_end_timestamp = end_timestamp

    return final_moments


if __name__ == "__main__":
    with open("data/AgbeGFYluEA/output.txt") as f:
        text = f.read()
    parsed_data = adjust_moments_timestamps(parse_file(remove_tabulations_and_lists(text)))
    # print(parsed_data)
    for data in parsed_data:
        print(data["start_timestamp"], data["end_timestamp"])

