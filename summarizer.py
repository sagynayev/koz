import json
import os
import re
from openai import OpenAI
from typing import List
from dotenv import load_dotenv


load_dotenv()

def load_transcript(path="output/transcript.json") -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Склеиваем сегменты в один текст
    text = "\n".join(
        seg["text"] for seg in data["segments"]
    )

    return text

def safe_json_parse(text: str):
    """
    Safely extract JSON object from LLM response
    (removes ```json blocks and extra text)
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM response")

    json_str = match.group(0)
    return json.loads(json_str)

SYSTEM_PROMPT = """
You are an AI meeting assistant.

Your task:
- Analyze a meeting transcript
- Extract summary, topics, decisions, and tasks

CRITICAL LANGUAGE RULE:
- The transcript may be in any language
- ALWAYS return the final output in RUSSIAN
- Do NOT translate names, product names, or technical terms
- Preserve the original meaning accurately

Rules:
- Be concise and factual
- Do NOT invent information
- Tasks must be actionable
- If owner is unknown, set owner = "TBD"
- If deadline is unknown, set deadline = null
- Priority must be one of: low, medium, high

Return STRICT JSON only.
"""

MEETING_TEMPLATES = {
    "team": "Team sync / internal discussion",
    "standup": "Daily standup",
    "sales": "Sales call with client",
    "planning": "Sprint / project planning"
}

client = OpenAI()

def summarize_meeting(transcript_text: str, meeting_type="team"):
    prompt = f"""
    Meeting type: {MEETING_TEMPLATES.get(meeting_type, meeting_type)}

    Transcript:
    {transcript_text}

    Return JSON with fields:
    summary (string)
    topics (array)
    decisions (array)
    tasks (array of objects: task, owner, deadline, priority)
    """


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content
    print("=== RAW LLM OUTPUT ===")
    print(content)
    print("======================")
    return safe_json_parse(content)
    

def save_outputs(result):
    os.makedirs("output", exist_ok=True)

    with open("output/summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": result["summary"],
            "topics": result.get("topics", []),
            "decisions": result.get("decisions", [])
        }, f, ensure_ascii=False, indent=2)

    with open("output/tasks.json", "w", encoding="utf-8") as f:
        json.dump(
            result.get("tasks", []),
            f,
            ensure_ascii=False,
            indent=2
        )
def run(meeting_type="team"):
    text = load_transcript()
    result = summarize_meeting(text, meeting_type)
    save_outputs(result)
    return result
