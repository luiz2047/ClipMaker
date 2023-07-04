import json
import os
from pathlib import Path
from tqdm import tqdm

import whisper


def transcribe_audio_files(data_path):
    """
    Transcribes all audio files in the given directory and saves the transcription results in a JSON file.
    """
    dirs_count = sum(len(dirs) for _, dirs, _ in os.walk(data_path))
    with tqdm(total=dirs_count) as pbar:
        for subdir, dirs, files in os.walk(data_path):
            for file in files:
                if file.endswith(".mp3"):
                    try:
                        path = os.path.join(subdir, file)
                        model = whisper.load_model("small", device="cuda")
                        result = model.transcribe(path, verbose=False, word_timestamps=True, language='en')
                        with open(os.path.join(subdir, "transcribe.json"), "w") as f:
                            json.dump(result, f)
                    except Exception as e:
                        print(f"Error transcribing file {path}: {e}")
                        continue
            pbar.update(1)


if __name__ == "__main__":
    data_path = Path("data")
    transcribe_audio_files(data_path)
