# YouTube Video Remake with Whisper and ChatGPT

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

This project allows users to remake YouTube videos by generating subtitles using the Whisper model and creating titles and descriptions using ChatGPT. The pipeline is fully automatic and generates content seamlessly.

## Installation

Make sure you have Python 3.x installed. Install the required packages using pip:

```
pip install pytube tqdm moviepy whisper openai==0.27.8 tiktoken python-dotenv
```

Please note that you also need to have `ffmpeg` installed on your system.

## Usage

### IDE

1. Clone the repository to your local machine.
2. Open the project in your favorite IDE.
3. Set up your environment and install the required packages (as mentioned in the installation section).
4. Execute the `main.py` script, providing the necessary command-line arguments.

### Command Line Interface (CLI)

1. Clone the repository to your local machine.
2. Open a terminal or command prompt.
3. Navigate to the project directory.
4. Install the required packages (as mentioned in the installation section).
5. Run the following command:

```
python main.py -d <data_directory> -l <channel_link> -n <num_videos> -m <mode> --whisper_model <model_name> --cuda <cuda> --gpt_model <gpt_model>
```

Replace the placeholders (`<data_directory>`, `<channel_link>`, etc.) with appropriate values.

## Output

After running the `main.py` script, the following outputs will be generated:

- Downloaded video from YouTube in MP4 and MP3 formats.
- Subtitles for the videos.
- Metadata of the video.
- The `results` folder will contain cropped videos with added subtitles.

## Example

1. Clone the repository to your local machine.
2. Install the required packages using pip (as mentioned in the installation section).
3. Run the following command:

```
python main.py -d data -l https://www.youtube.com/@Vsauce -n 10 -m full --whisper_model small --cuda cuda --gpt_model gpt-3.5-turbo
```

## Customization

Users can customize the resulting videos by modifying the `video_creator.py` file. Feel free to explore and experiment with the code to tailor the videos according to your preferences.

## Supported Models

The supported models for transcription can be found in the Whisper repository, and for GPT processing, you can refer to the OpenAI API documentation.

## Troubleshooting

In case you encounter any issues, please check the following:

- Ensure all dependencies are installed correctly.
- Verify that you have the necessary API keys and configurations for ChatGPT.
- Check for any reported issues in the GitHub repository.

## Contributing

Contributions are most welcome! If you'd like to contribute to the project, feel free to submit a pull request or open an issue on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify the ReadMe further to add more sections or adjust the content to better fit your project's specifics. Make sure to include any relevant badges, links, or visuals to enhance the overall appearance of your ReadMe. Good luck with your project!