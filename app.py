from flask import Flask

from lib.config import config

app = Flask(__name__)

@app.route('/')
def hello_world():
    return config.get('HELLO')

