import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

from audio_utils import normalize_audio
from asr import transcribe
from summarizer import run as summarize
from pdf_report import generate_pdf
from notion_integration import create_meeting_page

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    loop = asyncio.get_running_loop()

    await update.message.reply_text("Аудио получено. Начинаю обработку...")
    print("Audio received")

    # Определяем тип файла
    if update.message.voice:
        tg_file = await update.message.voice.get_file()
        ext = "ogg"

    elif update.message.audio:
        tg_file = await update.message.audio.get_file()
        ext = "mp3"

    elif update.message.document:
        tg_file = await update.message.document.get_file()
        ext = update.message.document.file_name.split(".")[-1]

    else:
        await update.message.reply_text("Неподдерживаемый формат аудио")
        return

    audio_path = f"/tmp/{tg_file.file_id}.{ext}"
    await tg_file.download_to_drive(audio_path)
    print(f"File downloaded: {audio_path}")

    # NORMALIZE (CPU ->thread)
    await update.message.reply_text("Нормализую аудио...")
    normalized = await loop.run_in_executor(
        None,
        normalize_audio,
        audio_path
    )
    print("Audio normalized")

    # TRANSCRIBE (CPU -> thread)
    await update.message.reply_text("Делаю транскрипцию...")
    await loop.run_in_executor(
        None,
        transcribe,
        normalized
    )
    print("Transcription done")

    # SUMMARIZE (LLM)
    await update.message.reply_text("Формирую саммари и задачи...")
    await loop.run_in_executor(
        None,
        summarize,
        "team"
    )
    print("Summary created")

    # PDF
    pdf_path = await loop.run_in_executor(
        None,
        generate_pdf
    )
    print("PDF generated")

    # NOTION
    await loop.run_in_executor(
        None,
        create_meeting_page,
        "team"
    )
    print("Notion page created")

    # SEND BACK
    await context.bot.send_document(
        chat_id=chat_id,
        document=open(pdf_path, "rb"),
        caption="Саммари встречи + задачи"
    )

    print("Report sent to Telegram")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    print("Starting Telegram bot...")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(
            filters.AUDIO | filters.VOICE | filters.Document.AUDIO,
            handle_audio
        )
    )

    print("Bot started. Waiting for audio...")
    application.run_polling(stop_signals=None)


if __name__ == "__main__":
    main()
