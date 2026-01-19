import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload)

def format_report():
    with open("output/summary.json", encoding="utf-8") as f:
        summary = json.load(f)

    with open("output/tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)

    message = "Итоги встречи\n\n"
    message += summary["summary"] + "\n\n"

    if tasks:
        message += "Задачи:\n"
        for i, task in enumerate(tasks, 1):
            prio = task.get("priority", "medium")
            message += f"{i}. {task['task']} ({prio})\n"
    else:
        message += "Задачи не зафиксированы."

    return message

def send_report(pdf_path: str):
    text = format_report()
    send_message(text)
    send_pdf(pdf_path)


def send_pdf(pdf_path: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

    with open(pdf_path, "rb") as f:
        files = {
            "document": f
        }
        data = {
            "chat_id": CHAT_ID,
            "caption": "Протокол встречи (PDF)"
        }
        requests.post(url, data=data, files=files)
