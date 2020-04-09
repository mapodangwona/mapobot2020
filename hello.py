import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def helloto():
    return 'Hello, world?'
