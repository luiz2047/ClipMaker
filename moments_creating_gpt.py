import json
import os
import time
from pathlib import Path
import openai
import tiktoken
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

openai.api_key = os.environ.get("OPENAI-API-KEY")


def get_title(metadata: dict):
    title = metadata['title']
    return title


def get_subtitles(transcribe: dict):
    subtitles = transcribe['segments']
    return subtitles


def format_subtitles(subtitles: list):
    formatted_subtitles = []
    for subtitle in subtitles:
        start_time = format_seconds_to_minutes_seconds(float(subtitle["start"]))
        end_time = format_seconds_to_minutes_seconds(float(subtitle["end"]))
        text = subtitle["text"]
        formatted_subtitles.append(f"{start_time}->{end_time}: {text}")
    return formatted_subtitles


def format_seconds_to_minutes_seconds(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02}"


def call_openai_api(model, prompt):
    max_retries = 3  # Maximum number of retries
    for retry in range(max_retries):
        try:
            completion = openai.ChatCompletion.create(model=model, messages=[{"role": "user", "content": prompt}])
            return completion.choices[0].message['content']
        except Exception as e:
            print(f"API Error: {e}")
            print(f"Retry attempt {retry + 1}/{max_retries}")
            time.sleep(2 ** retry)  # Wait for an exponentially increasing time before retrying
    return None  # If all retries fail, return None


def process_folder(folder_path):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    if os.path.isfile(folder_path / "output.txt"):
        print(f"{folder_path} already processed")
        return
    # Load metadata and transcribe data for the folder
    metadata_file_path = folder_path / "metadata.json"
    metadata = json.load(metadata_file_path.open())
    title = get_title(metadata)
    transcribe_file_path = folder_path / "transcribe.json"
    transcribe = json.load(transcribe_file_path.open())
    subtitles = format_subtitles(get_subtitles(transcribe))

    completion_list = []
    # Load the initial prompt template from a file
    with open("prompts/sample_prompt.txt") as file:
        prompt_template = file.read()

    # Prepare the full prompt with blocks of subtitles
    max_subtitles_per_block = 140
    num_blocks = (len(subtitles) + max_subtitles_per_block - 1) // max_subtitles_per_block
    print("Start processing folder:", folder_path)
    for i in tqdm(range(num_blocks)):
        full_prompt = ""
        block_subtitles = subtitles[i * max_subtitles_per_block: (i + 1) * max_subtitles_per_block]
        subtitle_block = "\n".join(block_subtitles)
        prompt = prompt_template.format(title=title, subtitles=subtitle_block)

        # Use tiktoken to check the length of the prompt
        prompt_length = len(enc.encode(prompt))

        # Check if the prompt length exceeds the model's maximum limit (4096 for gpt-3.5-turbo)
        if prompt_length > 4096:
            print("The prompt is too long for the model to handle.")
            continue

        full_prompt += prompt + "\n"

        completion_result = call_openai_api(model="gpt-3.5-turbo", prompt=full_prompt)

        # Call the API with retries
        if completion_result is not None:
            completion_list.append(completion_result)
        else:
            print("API call failed even after retries. Skipping this block.")

    # Save the generated answer in a file inside the folder
    output_file_path = folder_path / "output.txt"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(completion_list))


if __name__ == "__main__":
    data_folder = Path("data")
    for folder in tqdm(os.listdir(data_folder)):
        folder_path = data_folder / folder
        if os.path.isdir(folder_path):
            process_folder(folder_path)
