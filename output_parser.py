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
    t = datetime.strptime(timestamp, '%M:%S')
    return t.minute * 60 + t.second


def convert_seconds_to_timestamp(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f'{minutes:02}:{seconds:02}'


def adjust_moments_timestamps(moments):
    corrected_moments = []
    prev_end_timestamp = None

    for moment in moments:
        start_timestamp = convert_timestamp_to_seconds(moment['start_timestamp'])
        end_timestamp = convert_timestamp_to_seconds(moment['end_timestamp'])

        if prev_end_timestamp is not None and start_timestamp - prev_end_timestamp > 30:
            # If the gap between moments is too large, create a new moment using data from the previous one
            corrected_moments[-1]['end_timestamp'] = convert_seconds_to_timestamp(prev_end_timestamp + 60)
            start_timestamp = prev_end_timestamp + 60

        moment['start_timestamp'] = convert_seconds_to_timestamp(start_timestamp)
        moment['end_timestamp'] = convert_seconds_to_timestamp(end_timestamp)

        corrected_moments.append(moment)
        prev_end_timestamp = end_timestamp

    return corrected_moments


if __name__ == "__main__":
    with open("data/ACUuFg9Y9dY/output.txt") as f:
        text = f.read()
    parsed_data = remove_tabulations_and_lists(text)
    # print(parsed_data)
    print(adjust_moments_timestamps(parse_file(text)))
