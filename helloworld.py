import json
import os
from flask import Flask, request, make_response, jsonify

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


@app.route('/webhook', methods=['POST'])
def webhook():
    params = request.get_json(force=True)

    intent = params['queryResult']['intent']['displayName']
    if intent == 'candidate':
        candidatename = params['queryResult']['parameters']['candidatename']
        data = _load_data()['candidate'][candidatename]
        return {'fulfillment_messages': [
            {'text': data['text']},
            {'image': data['image']}
            {'link_out_suggestion': {'destination_name': '더보기', 'uri': data['url'}}
        ]}
    else:
        return {'fulfillmentText': '챗봇이 이해할 수 없는 내용이어요 ㅠㅠ'}
