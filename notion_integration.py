import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def create_meeting_page(meeting_type: str):
    with open("output/summary.json", encoding="utf-8") as f:
        summary = json.load(f)

    with open("output/tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)

    tasks_text = "\n".join(
        f"- {t['task']} (priority: {t['priority']})"
        for t in tasks
    )

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": "Meeting Summary"}}
                ]
            },
            "Type": {
                "select": {
                    "name": meeting_type.strip().lower()
                }
            },
            "Summary": {
                "rich_text": [
                    {"text": {"content": summary["summary"]}}
                ]
            },
            "Tasks": {
                "rich_text": [
                    {"text": {"content": tasks_text}}
                ]
            }
        }
    }

    r = requests.post(
        "https://api.notion.com/v1/pages",
        headers=HEADERS,
        json=payload
    )

    if not r.ok:
        print("Notion error:", r.status_code)
        print(r.text)

    r.raise_for_status()
