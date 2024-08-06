from flask_socketio import emit, SocketIO

from ai_model.Llama_container import LlamaContainer

socketio = SocketIO()

llama = LlamaContainer()


def register_handlers():
    @socketio.on('question')
    def handle_event(json):
        llama_answer = llama.generate_answer(json['message'])
        json['message'] = llama_answer
        emit('answer', json)

    @socketio.on('connect')
    def onConnect():
        if llama.model is None:
            llama.initialize_model()
