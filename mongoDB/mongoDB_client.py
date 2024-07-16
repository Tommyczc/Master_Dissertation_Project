import gridfs
from pymongo import MongoClient
from marshmallow import ValidationError
from bson.objectid import ObjectId
from datetime import datetime
from mongoDB.schema.upload_record import UploadRecordSchema


def init_db(connection_string):
    client = MongoClient(connection_string)
    db = client['rdf_upload_data']
    fs = gridfs.GridFS(db)  # 初始化 GridFS
    return db, fs


class MongoDBInterface:
    def __init__(self, db, fs):
        self.db = db
        self.fs = fs
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
        return str(result.inserted_id), 200

    def get_upload_record(self, record_id):
        """Retrieves an upload record from the database by its ID."""
        try:
            collection = self.db.upload_records
            record = collection.find_one({'_id': ObjectId(record_id)})
            if record:
                # print(record)
                # convert ObjectId to string
                record['_id'] = str(record['_id'])
                if 'file_urls' in record:
                    record['file_urls'] = [
                        {'filename': self.fs.get(ObjectId(file_id)).filename, 'file_urls': str(file_id)}
                        for file_id in record['file_urls']
                    ]
            return record
        except Exception as e:
            print("Error: Exception while retrieving upload record")
            return None

    def get_all_records(self):
        collection = self.db.upload_records
        records = collection.find()
        result = []
        for record in records:
            result.append({
                "title": record.get("title"),
                "description": record.get("description"),
                "created_at": record.get("created_at"),
                "id": str(record.get("_id"))
            })
        return result

    def upload_file(self, files: []):
        file_ids = []
        for file in files:
            # 将文件存储到 GridFS 中
            file_id = self.fs.put(file, filename=file.filename)
            file_ids.append(str(file_id))
        return file_ids

    def get_file(self, file_id):
        try:
            file = self.fs.get(ObjectId(file_id))
            return file
        except gridfs.errors.NoFile:
            print(f"No file found with id: {file_id}")
            return None

    def get_files(self,file_ids):
        """
        get file content
        :param file_ids: list of file ids
        :return: list of file content
        """

        files_content = []

        for file_id in file_ids:
            try:
                file = self.fs.get(ObjectId(file_id))
                files_content.append(file.read())
            except Exception as e:
                print(f"Error retrieving file {file_id}: {e}")
                files_content.append(None)

        return files_content

    def delete_record_by_id(self, record_id):
        collection = self.db.upload_records
        record = collection.find_one({'_id': ObjectId(record_id)})
        if not record:
            return False, "Record not found"

        # 删除与记录关联的文件
        for file_id in record['file_urls']:
            self.fs.delete(ObjectId(file_id))

        # 删除记录
        collection.delete_one({'_id': ObjectId(record_id)})
        return True, "Record deleted successfully"