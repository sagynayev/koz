import subprocess
import os

def normalize_audio(input_path, output_path="output/normalized.wav"):
    os.makedirs("output", exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path
