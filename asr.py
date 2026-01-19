from faster_whisper import WhisperModel
import json
import os

MODEL_SIZE = "small" 

def transcribe(audio_path: str, out_path="output/transcript.json"):
    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="int8"
    )

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True
    )

    transcript = {
        "language": info.language,
        "duration": info.duration,
        "segments": []
    }

    for seg in segments:
        transcript["segments"].append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        })

    os.makedirs("output", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    return transcript
