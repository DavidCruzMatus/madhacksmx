import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)

@app.route('/')
def hello():
    return 'This is my flask application!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio = SocketIO(app)
    socketio.run(app, host='0.0.0.0', port=port)