import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from dotenv import load_dotenv

load_dotenv('1.env')

TG_WEBHOOK = os.environ.get('TG_WEBHOOK_URL')

def _make_pdf(summary, tasks):
    """Создаёт PDF из summary и tasks и возвращает BytesIO объект"""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont('Helvetica', 12)
    c.drawString(50, 750, summary.get('title','Meeting Summary'))
    y = 730
    for t in summary.get('topics', []):
        c.drawString(50, y, '- ' + (t.get('topic') or 'Topic'))
        y -= 20
        for p in t.get('points', []):
            c.drawString(60, y, '* ' + (p if isinstance(p, str) else str(p)))
            y -= 15
            if y < 80:
                c.showPage()
                y = 750
    c.drawString(50, y-10, 'Tasks:')
    y -= 30
    for task in tasks:
        c.drawString(
            60, y, 
            '- ' + task.get('title','(task)') + 
            ' | owner:' + str(task.get('owner','-')) +
            ' | due:' + str(task.get('due','-')) +
            ' | priority:' + str(task.get('priority','-'))
        )
        y -= 15
        if y < 80:
            c.showPage()
            y = 750
    c.save()
    buf.seek(0)
    return buf

def send_to_telegram(outdir, summary, tasks):
    if not TG_WEBHOOK:
        raise RuntimeError('TG_WEBHOOK_URL not set in .env')

    pdfbuf = _make_pdf(summary, tasks)
    files = {'document': ('meeting_summary.pdf', pdfbuf, 'application/pdf')}
    data = {}
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if chat_id:
        data['chat_id'] = chat_id

    resp = requests.post(TG_WEBHOOK, data=data, files=files, timeout=30)
    resp.raise_for_status()
    print('Telegram response:', resp.json())
    return resp.json()


if __name__ == "__main__":
    summary = {
        'title':'Встреча 01', 
        'topics':[{'topic':'Обсуждение','points':['Точка 1','Точка 2']}]
    }
    tasks = [
        {'title':'Сделать презентацию','owner':'Иван','due':'2025-10-10','priority':'High'}
    ]

    send_to_telegram(None, summary, tasks)
