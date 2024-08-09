from flask import request, current_app
from flask_login import current_user, AnonymousUserMixin
from flask_socketio import emit, SocketIO

from Common_tools.rdflib_graph_manager import graph_manager
from ai_model.Llama_container import LlamaContainer

socketio = SocketIO()

llama = LlamaContainer()


def register_handlers():
    @socketio.on('connect', namespace='/rdf_local')
    def rdf_local_connect(json):
        # print('graph uri:',request.args.get('graph_uri'))
        # if res_num==1, means success, 0 means cannot load the data from jena
        res_num = graph_manager.load_graph(request.args.get('graph_uri'))

    @socketio.on('query', namespace='/rdf_local')
    def rdf_local_query(json):
        res = graph_manager.query_graph(request.args.get('graph_uri'), json['query'])
        emit('answer', res)

    @socketio.on('disconnect', namespace='/rdf_local')
    def rdf_local_disconnect():
        graph_manager.unload_graph(request.args.get('graph_uri'))

    @socketio.on('update_query', namespace='/rdf_local')
    def rdf_local_update_query(json):
        # print("update query")
        #check user identity
        user = current_user
        if not user.is_authenticated:
            # print("unauth")
            emit("error", "Sorry, only the owner of data can fo the edition")
        else:
            record_id = request.args.get('graph_uri')
            db_interface = current_app.config['DB_INTERFACE']
            username = db_interface.get_username_by_record_id(record_id)
            if username == user.username:
                res = graph_manager.update_query_graph(request.args.get('graph_uri'), json['update_query'])
                if res == "Updated the data successfully":
                    emit("success", res)
                else:
                    emit("error", res)
            else:
                emit("error", "Sorry, only the owner of data can fo the edition")

    @socketio.on('question', namespace='/KGQA')
    def handle_event(json):
        llama_answer = llama.generate_answer(json['message'])
        json['message'] = llama_answer
        emit('answer', json)

    @socketio.on('connect', namespace='/KGQA')
    def onConnect():
        if llama.model is None:
            llama.initialize_model()
