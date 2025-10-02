import os, requests, json
from dotenv import load_dotenv
load_dotenv('1.env')

def create_notion_page(summary, tasks):
    token = os.environ.get('NOTION_TOKEN')
    database = os.environ.get('NOTION_DB')
    if not token:
        raise RuntimeError('NOTION_TOKEN not set')

    url = 'https://api.notion.com/v1/pages'
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    # Страница встречи
    body = {
        'parent': {'database_id': database} if database else {'type':'page_id','page_id': os.environ.get('NOTION_PARENT_PAGE','')},
        'properties': {
            'Name': {'title':[{'text':{'content':summary.get('title','Meeting')}}]}
        },
        'children': []
    }

    # Topics
    for topic in summary.get('topics', []):
        body['children'].append({
            'object':'block','type':'heading_2',
            'heading_2':{'text':[{'type':'text','text':{'content':topic.get('topic','Topic')}}]}
        })
        for p in topic.get('points', []):
            body['children'].append({
                'object':'block','type':'paragraph',
                'paragraph':{'text':[{'type':'text','text':{'content':str(p)}}]}
            })

    # Tasks → To-Do блоки
    for task in tasks:
        task_text = f"{task.get('title','Task')} | owner:{task.get('owner','-')} | due:{task.get('due','-')} | priority:{task.get('priority','-')}"
        body['children'].append({
            'object':'block','type':'to_do',
            'to_do':{
                'text':[{'type':'text','text':{'content':task_text}}],
                'checked': False
            }
        })

    resp = requests.post(url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()
