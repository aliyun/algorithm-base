from flask import Flask

app = Flask(__name__)

"""
gunicorn -w 1 -b 0.0.0.0:8000 hello:app
"""
@app.route('/')
def hello_world():
    return 'Hello World!'
