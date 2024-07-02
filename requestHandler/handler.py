from flask import render_template, Blueprint, request, jsonify, current_app, redirect, url_for

handler = Blueprint('handler', __name__)


@handler.route('/uploadRDF_request', methods=['post'])
def uploadRDF_request():
    # print("called")
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        rdf_files = request.files.getlist('rdf_files')
        # print("pa:   ",params)
        # print("value:   ",title, description)
        # print("file:   ",type(rdf_files))

        if not title or not rdf_files:
            return jsonify({"error": "Title and RDF file are required"}), 400

        db_interface = current_app.config['DB_INTERFACE']
        file_paths = db_interface.upload_file(rdf_files)
        # print("path: ", file_paths)

        data={'title': title, 'description': description, 'file_urls': file_paths}
        insert_id,code=db_interface.create_upload_record(data)
        print(insert_id,code)
        if code == 201:
            return jsonify({"success":insert_id}), 200
        else:
            return jsonify({"error":code}), 400
        # for file in rdf_files:
        #     print(file.filename) ## file name
        #     print(len(file.stream.read())) ## file size

    except Exception as e:
        return jsonify({"error": str(e)}), 500
