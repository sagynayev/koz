import os, tempfile, json
from pydub import AudioSegment
from dotenv import load_dotenv
load_dotenv("1.env")
def _ensure_wav(path):
    if path.lower().endswith('.wav'):
        return path
    # convert to wav
    audio = AudioSegment.from_file(path)
    out = tempfile.mktemp(suffix='.wav')
    audio.export(out, format='wav')
    return out

def transcribe_file(path, provider=None):
    """Transcribe audio file.
    - If OPENAI_API_KEY present, will call OpenAI's audio transcription endpoint.
    - Otherwise, attempt to use Vosk local model (if installed).
    Returns a transcript dict with segments.
    """
    provider = provider or os.environ.get('ASR_PROVIDER', 'auto')
    wav = _ensure_wav(path)
    # Prefer OpenAI if key available
    if os.environ.get('OPENAI_API_KEY') and provider in ('auto','openai'):
        return _transcribe_openai(wav)
    try:
        import vosk
        return _transcribe_vosk(wav)
    except Exception:
        return {
            'text': 'TRANSCRIPTION_NOT_AVAILABLE. Set OPENAI_API_KEY or install VOSK.',
            'segments': []
        }

from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def _transcribe_openai(wav_path):
    """Transcribe audio using OpenAI new API."""
    with open(wav_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f
        )
    text = resp.text
    return {"text": text, "segments": []}


def _transcribe_vosk(wav_path):
    import wave
    import vosk
    wf = wave.open(wav_path, "rb")
    model = vosk.Model(lang="ru-RU") # en-us
    rec = vosk.KaldiRecognizer(model, wf.getframerate())
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
    results.append(json.loads(rec.FinalResult()))
    text = ' '.join([r.get('text','') for r in results])
    return {'text': text, 'segments': []}
