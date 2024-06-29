from marshmallow import Schema, fields, validate, ValidationError


# define UploadRecordSchema
class UploadRecordSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False, validate=validate.Length(max=500))
    file_url = fields.String(required=True, validate=validate.URL())
    created_at = fields.DateTime(dump_only=True)
