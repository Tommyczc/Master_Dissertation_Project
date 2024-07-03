from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)


@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    send(message, room=room)


@socketio.on('private_message')
def handle_private_message(data):
    recipient_sid = data['recipient_sid']
    message = data['message']
    emit('private_message', message, to=recipient_sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
