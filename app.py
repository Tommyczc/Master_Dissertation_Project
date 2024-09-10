from flask import Flask
from flask_login import LoginManager, current_user
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed
from flask_socketio import SocketIO

from security.models import User
from socket_for_QA import socket_handler
from jena.fuseki_client import JenaClient
from mongoDB.mongoDB_client import init_db, MongoDBInterface
from requestHandler.handler import handler
from router.router import router
from security.auth import auth_bp

app = Flask(__name__)

# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
## register blueprint
app.register_blueprint(router)
app.register_blueprint(handler)
app.register_blueprint(auth_bp)

# ini database connection
# db, fs = init_db(
#     'mongodb+srv://tommy:!project22558800@disser.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256'
#     '&retrywrites=false&maxIdleTimeMS=120000')
db, fs = init_db("mongodb://localhost:27017")
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

login_manager = LoginManager(app)
principals = Principal(app)
login_manager.login_view = "auth.signIn"
@login_manager.user_loader
def load_user(user_id):

    user_data = db_interface.get_user_by_id(user_id)
    return user_data

# @identity_loaded.connect_via(app)
# def on_identity_loaded(sender, identity):
#     identity.user = current_user
#     if hasattr(current_user, 'id'):
#         identity.provides.add(UserNeed(current_user.id))
#     if hasattr(current_user, 'roles'):
#         for role in current_user.roles:
#             identity.provides.add(RoleNeed(role))


if __name__ == '__main__':
    # app.run()
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=8000,
        allow_unsafe_werkzeug=True
    )
