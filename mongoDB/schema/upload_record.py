from marshmallow import Schema, fields, validate, ValidationError


# define UploadRecordSchema
class UploadRecordSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False, validate=validate.Length(max=500))
    file_urls = fields.List(fields.String(), required=True)
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.String(required=True, validate=validate.Length(min=1, max=100))
    username = fields.String(required=True, validate=validate.Length(min=1, max=100))
