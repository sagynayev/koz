from audio_utils import normalize_audio
from asr import transcribe
from summarizer import run as summarize
from pdf_report import generate_pdf
from notion_integration import create_meeting_page
from tg_integration import send_report


def run_pipeline(audio_path: str, meeting_type: str = "team") -> str:
    """
    Runs full meeting processing pipeline.
    Returns path to generated PDF.
    Also sends report to Telegram.
    """

    normalized = normalize_audio(audio_path)
    transcribe(normalized)
    summarize(meeting_type)

    pdf_path = generate_pdf()
    create_meeting_page(meeting_type)

    return pdf_path
