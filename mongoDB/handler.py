from pymongo import MongoClient
from flask import Flask

def init_db(app: Flask):
    app.config["MONGO_URI"] = "mongodb://localhost:27017/your_database_name"
    mongo = PyMongo(app)
    return mongo

class MongoDBInterface:
    def __init__(self, mongo):
        self.mongo = mongo