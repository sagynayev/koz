# not need
import argparse
from audio_utils import normalize_audio
from asr import transcribe
from summarizer import run as summarize
from tg_integration import send_report
from pdf_report import generate_pdf
from notion_integration import create_meeting_page


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True)
    parser.add_argument("--meeting_type", default="team")
    args = parser.parse_args()

    print("Normalizing audio...")
    audio = normalize_audio(args.audio)
    pdf_path = generate_pdf()

    print("Transcribing...")
    transcript = transcribe(audio)
    print("Summarizing...")
    summarize(args.meeting_type)
    print("Writing to Notion...")
    create_meeting_page(args.meeting_type)
    print("Sending report to Telegram...")
    send_report(pdf_path)


    print("summary.json + tasks.json created")

    print("Done. Transcript saved to output/transcript.json")

if __name__ == "__main__":
    main()
