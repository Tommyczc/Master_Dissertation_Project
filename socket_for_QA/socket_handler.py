from flask_socketio import emit, SocketIO

socketio = SocketIO()


def questions(json):
    print(json)
    emit('answer', json)


def register_handlers():
    @socketio.on('question')
    def handle_event(data):
        questions(data)
