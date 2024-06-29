from pymongo import MongoClient
from marshmallow import ValidationError
from bson.objectid import ObjectId
from datetime import datetime
from mongoDB.schema.upload_record import UploadRecordSchema

def init_db():
    client = MongoClient('mongodb+srv://tommy:!project22558800@disser.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000')
    db = client['rdfData']
    return db



class MongoDBInterface:
    def __init__(self, db):
        self.db = db
        self.upload_record_schema = UploadRecordSchema()

    def create_upload_record(self, data):
        """Creates a new upload record in the database."""
        # 验证数据
        try:
            validated_data = self.upload_record_schema.load(data)
            validated_data['created_at'] = datetime.utcnow()  # 添加创建时间
        except ValidationError as err:
            return {"error": err.messages}, 400

        collection = self.db.upload_records
        result = collection.insert_one(validated_data)
        return str(result.inserted_id), 201

    def get_upload_record(self, record_id):
        """Retrieves an upload record from the database by its ID."""
        collection = self.db.upload_records
        try:
            record = collection.find_one({"_id": ObjectId(record_id)})
        except Exception as e:
            return None

        return record

    # 其他数据库操作可以在这里定义
