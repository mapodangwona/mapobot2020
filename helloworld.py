"""Simple Flask webserver to handle chatbot request."""
import json
import os
import traceback

from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, world!'

DATA = None
def _load_data():
    global DATA
    if not DATA:
        with open('data.json', 'r') as ifile:
            DATA = json.load(ifile)
    return DATA


def build_fulfillment(data):
    messages = []
    if isinstance(data, dict):
        if 'text' in data:
            messages.append({'text': {'text': [data['text']]}})
        if 'image' in data:
            messages.append({'image': {'image_uri': data['image']}})
        if 'url' in data:
            if isinstance(data['url'], str):
                urls = [{'더 보기 (Link)': data['url']}]
            else:
                urls = data['url']
            for url in urls:
                for key, value in url.items():
                    display = f'<a href="{value}">key (Link)</a>'
                    messages.append({'text': {'text': [display], 'parse_mode': 'HTML', 'disable_web_preview': True}})
        return {'fulfillment_messages': messages}
    else:
        return {'fulfillmentText': '챗봇이 이해할 수 없는 내용이어요 ㅠㅠ'}


@app.route('/webhook', methods=['POST'])
def webhook():
    params = request.get_json(force=True)
    try:
        intent = params['queryResult']['intent']['displayName']
        intent_param_map = _load_data()['intent_param_map']
        parameter = params['queryResult']['parameters'][intent_param_map[intent]]
        return build_fulfillment(_load_data()[intent][parameter])
    except Exception as exc:
        if False:
            return {'fulfillmentText': '챗봇 속에서 에러가 났네요 ㅠㅠ'}
        else:
            return {'fulfillmentText': traceback.format_exc()}


@app.route('/privacy')
def privacy():
    return 'Privacy policy under construction'


@app.route('/eula')
def eula():
    return 'End-user License Agreement under construction'

