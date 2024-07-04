from flask_socketio import join_room, leave_room, send, emit
from app import socketio
from rdflib import Graph
from flask import current_app

# 缓存房间的RDFLib实例
room_graphs = {}


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)

    # 从MongoDB获取上传记录
    db_interface=current_app.config['DB_INTERFACE']
    upload_record = db_interface.get_upload_record(room)
    if upload_record:
        g = Graph()
        for file_url in upload_record['file_urls']['file_id']:
            g.parse(file_url)

        # 缓存RDFLib实例
        room_graphs[room] = g

    send(f'{username} has entered the room.', room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f'{username} has left the room.', room=room)


@socketio.on('sparql_query')
def handle_sparql_query(data):
    room = data['room']
    query = data['query']
    username = data['username']

    # 执行SPARQL查询
    g = room_graphs.get(room)
    if g:
        qres = g.query(query)
        results = []
        for row in qres:
            results.append(row.asdict())

        # 私发结果
        emit('sparql_result', {'results': results})
    else:
        emit('sparql_result', {'error': 'Room not initialized'})
