import re


def remove_tabulations_and_lists(text):
    text_without_multiple_enter = re.sub(r'\n+', '\n', text)
    text_without_lists = re.sub(r'\d+\.\s*', '', text_without_multiple_enter)
    text_without_tabs = text_without_lists.replace("\t", "")
    lines = text_without_tabs.split('\n')
    clean_lines = [line.strip() for line in lines]
    cleaned_text = '\n'.join(clean_lines)

    return cleaned_text


def parse_file(file_content):
    file_content = remove_tabulations_and_lists(file_content)
    pattern = r'(?:Title(?: of moment)?: )?(.*?)\nHashtags: (.*?)\nDescription: (.*?)\nTimestamp: ([0-9:]+)->([0-9:]+)'
    matches = re.findall(pattern, file_content, re.DOTALL)
    parsed_data = []

    for match in matches:
        title = match[0]
        hashtags = [tag.strip() for tag in match[1].split()]
        description = match[2]
        start_timestamp = match[3]
        end_timestamp = match[4]

        parsed_data.append({
            'title': title,
            'hashtags': hashtags,
            'description': description,
            'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp
        })

    return parsed_data


if __name__ == "__main__":
    with open("data/1RHsAUyFCAM/output.txt") as f:
        parsed_data = parse_file(f.read())
        print(parsed_data)
