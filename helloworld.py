import json
import os
from flask import Flask, request, make_response, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, world!'

@app.route('/webhook', methods=['POST'])
def webhook():
    params = request.get_json(force=True)
    
    with open('data.json', 'r') as ifile:
        data = json.load(ifile)

    result = {'got': json.dumps(params), 'release': data['releaseDate']}

    return {'fulfillmentText': json.dumps(result)}
