import os
import argparse
import time
from flask import Flask, request, render_template_string, jsonify
from asr import transcribe_file
from summarizer import summarize_transcript
from tg_integration import send_to_telegram
from notion_integration import create_notion_page
from pathlib import Path
import json
from dotenv import load_dotenv

load_dotenv('1.env')
app = Flask(__name__)

UPLOAD_HTML = '''<!doctype html>
<title>Meetings → Tasks MVP</title>
<h2>Upload audio (wav/mp3)</h2>
<form method=post enctype=multipart/form-data action="/upload">
  <input type=file name=file><br><br>
  Meeting type:
  <select name="mtype">
    <option>team meeting</option>
    <option>standup</option>
    <option>sales call</option>
    <option>auto</option>
  </select><br><br>
  <input type=submit value=Upload>
</form>
'''

@app.route('/')
def index():
    return render_template_string(UPLOAD_HTML)

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    mtype = request.form.get('mtype', 'auto')
    if not f:
        return "No file", 400
    outdir = Path('output') / str(int(time.time()))
    outdir.mkdir(parents=True, exist_ok=True)
    filepath = outdir / f.filename
    f.save(filepath)

    transcript = transcribe_file(str(filepath))
    with open(outdir / 'transcript.json', 'w', encoding='utf-8') as fh:
        json.dump(transcript, fh, ensure_ascii=False, indent=2)

    summary, tasks = summarize_transcript(transcript, meeting_type=mtype)
    with open(outdir / 'summary.json', 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    with open(outdir / 'tasks.json', 'w', encoding='utf-8') as fh:
        json.dump(tasks, fh, ensure_ascii=False, indent=2)

    try:
        send_to_telegram(outdir, summary, tasks)
    except Exception as e:
        print('TG send failed:', e)
    try:
        create_notion_page(summary, tasks)
    except Exception as e:
        print('Notion create failed:', e)

    return jsonify({
        'transcript': str(outdir / 'transcript.json'),
        'summary': str(outdir / 'summary.json'),
        'tasks': str(outdir / 'tasks.json')
    })


def cli_main(args):
    filepath = args.input
    mtype = args.type or 'auto'
    outdir = Path('output') / str(int(time.time()))
    outdir.mkdir(parents=True, exist_ok=True)

    transcript = transcribe_file(filepath)
    with open(outdir / 'transcript.json', 'w', encoding='utf-8') as fh:
        json.dump(transcript, fh, ensure_ascii=False, indent=2)

    summary, tasks = summarize_transcript(transcript, meeting_type=mtype)
    with open(outdir / 'summary.json', 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    with open(outdir / 'tasks.json', 'w', encoding='utf-8') as fh:
        json.dump(tasks, fh, ensure_ascii=False, indent=2)

    print('Output written to', outdir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Path to audio file for CLI mode')
    parser.add_argument('--type', help='Meeting type', default='auto')
    parser.add_argument('--serve', action='store_true', help='Run web server')
    args = parser.parse_args()

    if args.serve:
        app.run(debug=True)
    elif args.input:
        cli_main(args)
    else:
        print('Run with --serve for web UI or --input <audiofile> for CLI')
