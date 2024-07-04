from flask import Flask
from flask_socketio import SocketIO
from router.router import router
from requestHandler.handler import handler
from mongoDB.mongoDB_client import init_db, MongoDBInterface
from jena.fuseki_client import JenaClient
import socket

app = Flask(__name__)

## register blueprint
app.register_blueprint(router)
app.register_blueprint(handler)

# ini database connection
db, fs = init_db()
db_interface = MongoDBInterface(db, fs)
# store db_interface object in app config
app.config['DB_INTERFACE'] = db_interface

# ini Jena client
# jena_client = JenaClient(jena_url='http://ec2-18-134-209-210.eu-west-2.compute.amazonaws.com:3030', dataset='test') #hosted in aws
jena_client = JenaClient(jena_url='http://127.0.0.1:3030', dataset='test') ##local
app.config['JENA_CLIENT']=jena_client


# ini websocket
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)

if __name__ == '__main__':
    app.run()
