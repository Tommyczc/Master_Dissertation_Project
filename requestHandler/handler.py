import io

from flask import Blueprint, request, jsonify, current_app, redirect, url_for, send_file

handler = Blueprint('handler', __name__)


@handler.route('/uploadRDF_request', methods=['post'])
def uploadRDF_request():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        rdf_files = request.files.getlist('rdf_files')

        if not title or not rdf_files:
            return jsonify({"error": "Title and RDF file are required"}), 400

        ##todo: add mongodb session rollback, if fuseki return error response, then rollback the data

        ## upload the file to mongodb
        db_interface = current_app.config['DB_INTERFACE']
        file_paths = db_interface.upload_file(rdf_files)
        # print("path: ", file_paths)

        ## upload the record to mongodb
        data = {'title': title, 'description': description, 'file_urls': file_paths}
        insert_id, code = db_interface.create_upload_record(data)
        if code != 200:
            return jsonify({"error": code}), 400

        ## upload the rdf file to jena server
        rdf_data_list = []
        for rdf_file in rdf_files:
            filename = rdf_file.filename
            rdf_file.seek(0)  # ensure the reader pointer in start(0) location
            content = rdf_file.read().decode('utf-8')
            if filename.endswith('.rdf'):
                rdf_type = 'xml'
            elif filename.endswith('.ttl'):
                rdf_type = 'turtle'
            elif filename.endswith('.nt'):
                rdf_type = 'nt'
            elif filename.endswith('.n3'):
                rdf_type = 'n3'
            else:
                print("Error: unsupported file type: {}".format(filename))
                return jsonify({'error': f'Unsupported file type: {filename}'}), 400
            rdf_data_list.append({'content': content, 'type': rdf_type})

        jenaClient = current_app.config['JENA_CLIENT']
        res_code, res_content = jenaClient.upload_rdf_files(rdf_data_list, insert_id)
        if res_code >= 300:
            return jsonify({"error": res_content}), res_code

        # print("upload success, id: {}".format(insert_id))
        return jsonify({"success": insert_id}), 200

    except Exception as e:
        print("Error: ", str(e))
        return jsonify({"error": str(e)}), 500


@handler.route('/sparQL_query', methods=['post'])
def sparQL_query():
    try:
        req = request.get_json()
        jenaClient = current_app.config['JENA_CLIENT']
        res_code, res_content = jenaClient.execute_sparql_query_global(req['query'])
        if res_code >= 300:
            return jsonify({"error": res_content}), res_code
        return jsonify({"success": res_content}), 200
    except Exception as e:
        print("Error: ", str(e))
        return jsonify({"error": str(e)}), 500


@handler.route('/download/<file_id>', methods=['get'])
def download_file(file_id):
    db_interface = current_app.config['DB_INTERFACE']
    file = db_interface.get_file(file_id)
    if not file:
        return "File not found", 404
    return send_file(
        io.BytesIO(file.read()),
        download_name=file.filename,
        as_attachment=True
    )


@handler.route('/deleteRDF_request/<file_id>', methods=['get'])
def deleteRDF_request(file_id):
    # try:
    jenaClient = current_app.config['JENA_CLIENT']
    code, text = jenaClient.delete_rdf_by_record_id(file_id)
    print(code, text)
    #todo: delete the record from mongodb
    return jsonify({"error": text}), code
    # if status_code >= 300:
    #     print("error: ", text)
    #     return jsonify({"error": text}), status_code
    # else:
    #     return jsonify({"success": True}), 200
    # except Exception as e:
    #     print("fail: ", str(e))
    #     return jsonify({"error": str(e)}), 500
