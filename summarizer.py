import os, json, re
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
load_dotenv('1.env')

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

DEFAULT_PROMPT = """
You are a meeting assistant AI. Given the transcript, you must:
1) Summarize key topics.
2) Extract actionable tasks (even implied ones) with:
   - title
   - owner (who should do it)
   - due date (if mentioned, otherwise suggest)
   - priority (low/medium/high)
   - notes (context from discussion)

Meeting type: {meeting_type}
Transcript:
{transcript}

Output STRICT JSON ONLY, keys: title, topics, tasks.
"""

def extract_json_from_text(text):
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            return None
    return None

def summarize_transcript(transcript, meeting_type='auto'):
    text = transcript.get('text') or ''
    prompt = DEFAULT_PROMPT.format(transcript=text, meeting_type=meeting_type)
    resp = client.chat.completions.create(
        model=os.environ.get('OPENAI_MODEL','gpt-4o-mini'),
        messages=[{'role':'user','content':prompt}],
        max_tokens=1500
    )
    content = resp.choices[0].message.content
    parsed = extract_json_from_text(content)
    
    if parsed:
        title = parsed.get('title','Meeting summary')
        topics = parsed.get('topics',[])
        tasks = parsed.get('tasks',[])
    else:
        title = 'Meeting summary'
        topics = [{'topic':'Summary','points':[content[:500]]}]
        tasks = []

    summary = {
        'title': title,
        'meeting_type': meeting_type,
        'generated_at': datetime.utcnow().isoformat(),
        'topics': topics
    }
    return summary, tasks
