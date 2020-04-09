"""Simple Flask webserver to handle chatbot request."""
import json
import time
import traceback

from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    return 't.me/mapodangwon_2020_bot'


DATA = None
def _load_data():
    global DATA
    if not DATA:
        with open('data.json', 'r') as ifile:
            DATA = json.load(ifile)
    return DATA

DEBUGGING_NOW = True


def build_fulfillment(data: dict, result: dict, is_google: bool):
    messages = result['fulfillment_messages']
    if 'text' in data:
        messages.append({'text': {'text': [data['text']]}})
    if 'image' in data:
        messages.append({'image': {'image_uri': data['image']}})
    if 'url' in data:
        if isinstance(data['url'], str):
            urls = [{'정보 더 보기': data['url']}]
        else:
            urls = data['url']
        for url in urls:
            for key, value in url.items():
                display = f'<a href="{value}">{key} (Link)</a>'
                if is_google:
                    messages.append({'text': {'text': [display]}})
                else:
                    messages.append({'payload': {
                        'telegram': {'text': [display], 'parse_mode': 'HTML',
                                     'disable_web_page_preview': True}}})


@app.route('/webhook', methods=['POST'])
def webhook():
    params = request.get_json(force=True)
    try:
        intent = params['queryResult']['intent']['displayName']
        intent_param_map = _load_data()['intent_param_map']
        result = {'fulfillment_messages': [], 'fulfillmentText': ""}
        is_google = False
        if 'originalDetectIntentRequest' in params:
            if 'source' not in params['originalDetectIntentRequest']:
                is_google = True
            elif params['originalDetectIntentRequest'] in ['google', 'agent']:
                is_google = True
        else:
            is_google = True
        if intent_param_map[intent] not in params['queryResult']['parameters']:
            parameter = ''
        else:
            parameter = params['queryResult']['parameters'][intent_param_map[intent]]
            if parameter not in params['queryResult']['queryText']:
                result['fulfillment_messages'].append({'text': {'text': [
                    f'입력하신 내용은 {parameter} 관련으로 보여요!']}})
        build_fulfillment(_load_data()[intent][parameter], result, is_google)
        return result
    except Exception:  # pylint: disable=broad-except
        if not DEBUGGING_NOW:
            return {'fulfillmentText': '챗봇 속에서 에러가 났네요 ㅠㅠ'}
        else:
            return {'fulfillmentText': traceback.format_exc()}


@app.route('/privacy')
def privacy():
    return 'Privacy policy under construction'


@app.route('/eula')
def eula():
    return 'End-user License Agreement under construction'

