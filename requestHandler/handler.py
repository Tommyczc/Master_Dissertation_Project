from flask import render_template, Blueprint, request, jsonify

handler = Blueprint('handler', __name__)


@handler.route('/uploadRDF_request', methods=['post'])
def uploadRDF_request():
    print("called")
    try:
        params = request.form.to_dict()
        title = request.form.get('title')
        description = request.form.get('description')
        rdf_files = request.files.getlist('rdf_files')
        # print("pa:   ",params)
        # print("value:   ",title, description)
        # print("file:   ",rdf_files)

        if not title or not rdf_files:
            return jsonify({"error": "Title and RDF file are required"}), 400

        for file in rdf_files:
            print(file.filename) ## file name
            print(len(file.stream.read())) ## file size

        return jsonify({"success"}),200
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500
