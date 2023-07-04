import json
import os
from pathlib import Path
from tqdm import tqdm
import whisper


class TranscriptionProcessor:
    def __init__(self, model_name="small", device="cuda"):
        self.model_name = model_name
        self.device = device

    def transcribe_audio_file(self, audio_file_path):
        """
        Transcribes a single audio file and saves the transcription result in a JSON file.
        """
        try:
            model = whisper.load_model(self.model_name, device=self.device)
            result = model.transcribe(audio_file_path, verbose=False, word_timestamps=True, language='en')
            output_path = audio_file_path.parent / "transcribe.json"
            with open(output_path, "w") as f:
                json.dump(result, f)
        except Exception as e:
            print(f"Error transcribing file {audio_file_path}: {e}")

    def transcribe_audio_files(self, data_path):
        """
        Transcribes all audio files in the given directory and saves the transcription results in JSON files.
        """
        dirs_count = sum(len(dirs) for _, dirs, _ in os.walk(data_path))
        with tqdm(total=dirs_count) as pbar:
            for subdir, dirs, files in os.walk(data_path):
                for file in files:
                    if file.endswith(".mp3"):
                        audio_file_path = Path(subdir) / file
                        self.transcribe_audio_file(audio_file_path)
                pbar.update(1)


if __name__ == "__main__":
    data_path = Path("data")
    processor = TranscriptionProcessor(model_name="small", device="cuda")
    processor.transcribe_audio_files(data_path)