from flask_socketio import SocketIO, emit
from flask import Flask


class Tarasp:

    def __init__(self, port: int):
        self.port = port
        self.app = Flask(__name__)
        self.app.config['PORT'] = port
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, logger=True, engineio_logger=True, cors_allowed_origins='*')

    def run(self):
        self.socketio.run(self.app)
