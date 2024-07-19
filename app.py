from flask import Flask
from flask_socketio import SocketIO
from socket_for_QA import socket_handler
from jena.fuseki_client import JenaClient
from mongoDB.mongoDB_client import init_db, MongoDBInterface
from requestHandler.handler import handler
from router.router import router

app = Flask(__name__)

# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
## register blueprint
app.register_blueprint(router)
app.register_blueprint(handler)

# ini database connection
# db, fs = init_db(
#     'mongodb+srv://tommy:!project22558800@disser.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256'
#     '&retrywrites=false&maxIdleTimeMS=120000')
db, fs = init_db(
    "mongodb://localhost:27017")
db_interface = MongoDBInterface(db, fs)
# store db_interface object in app config
app.config['DB_INTERFACE'] = db_interface


# ini Jena client
# jena_client = JenaClient(jena_url='http://ec2-18-134-209-210.eu-west-2.compute.amazonaws.com:3030',
# dataset='test') #this url is hosted in aws
jena_client = JenaClient(jena_url='http://127.0.0.1:3030', dataset='test')  ##local
app.config['JENA_CLIENT'] = jena_client


# ini socket_for_QA
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socket_handler.socketio = socketio
socket_handler.register_handlers()

if __name__ == '__main__':
    # app.run()
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=8000,
        allow_unsafe_werkzeug=True
    )
