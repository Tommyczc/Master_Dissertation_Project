from flask import Flask
from router.router import router
from requestHandler.handler import handler
from mongoDB.controller import init_db, MongoDBInterface

app = Flask(__name__)

## register blueprint
app.register_blueprint(router)
app.register_blueprint(handler)

# ini database connection
db, fs = init_db()
db_interface = MongoDBInterface(db, fs)

# store db_interface object in app config
app.config['DB_INTERFACE'] = db_interface

if __name__ == '__main__':
    app.run()
