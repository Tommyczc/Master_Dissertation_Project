import io

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user

from Common_tools import rdf_tools
from socket_for_QA import socket_handler

handler = Blueprint('handler', __name__)


@handler.route('/uploadRDF_request', methods=['post'])
@login_required
def uploadRDF_request():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        rdf_files = request.files.getlist('rdf_files')
        user = current_user
        user_id = user.id
        username = user.username
        if not title or not rdf_files:
            return jsonify({"error": "Title and RDF file are required"}), 400

        ##todo: add mongodb session rollback, if fuseki return error response, then rollback the data

        ## upload the file to mongodb
        db_interface = current_app.config['DB_INTERFACE']
        file_paths = db_interface.upload_file(rdf_files)
        # print("path: ", file_paths)

        ## upload the record to mongodb
        data = {'title': title, 'description': description, 'file_urls': file_paths, 'user_id': user_id,
                'username': username}
        insert_id, code = db_interface.create_upload_record(data)
        # print("insert id:",insert_id)
        if code != 200:
            print("error: could not create upload record in mongodb")
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
        if res_code != 200:
            # print("error: {}".format(res_content))
            return jsonify({"error": res_content}), res_code

        # update the data in llama
        socket_handler.llama.generate_system_message()
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
            print("Error: ", res_code, res_content)
            return res_content, res_code
        # print(res_content)
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
    try:
        # delete the rdf data from jena
        jenaClient = current_app.config['JENA_CLIENT']
        code, text = jenaClient.delete_rdf_by_record_id(file_id)
        # print(code, text)
        if code >= 300:
            print("Error: ", code, text)
            return jsonify({"error": text}), code

        # delete the record and files from mongodb
        db_interface = current_app.config['DB_INTERFACE']
        result, text = db_interface.delete_record_by_id(file_id)
        if result is False:
            print("Error: ", result, text)
            return jsonify({"error": text}), 500

        return jsonify({"success": "record has been deleted."}), 200
    except Exception as e:
        print("fail: ", str(e))
        return jsonify({"error": str(e)}), 500


@handler.route('/sparQL_query_single_record/<subpath>', methods=['post'])
def sparQL_query_single_record(subpath):
    try:
        req = request.get_json()
        jenaClient = current_app.config['JENA_CLIENT']
        res_code, res_text = jenaClient.execute_sparql_query_for_graph(subpath, req['query'])
        if res_code >= 300:
            print("Error: ", res_code, res_text)
            return jsonify({"error": res_text}), res_code
        return jsonify({"success": res_text}), 200

    except Exception as e:
        print("Error: ", str(e))
        return jsonify({"error": str(e)}), 500


@handler.route('/generate_graph/<subpath>', methods=['GET'])
def generate_graph(subpath):
    jenaClient = current_app.config['JENA_CLIENT']
    rdf_data = jenaClient.get_rdf_data_for_graph(subpath)
    nodes, edges = rdf_tools.transfer_RDF_to_graph(rdf_data)
    return jsonify(nodes=nodes, edges=edges)
