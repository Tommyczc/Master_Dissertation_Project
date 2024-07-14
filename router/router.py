from flask import render_template, Blueprint, current_app, redirect, url_for

router = Blueprint('router', __name__)


@router.route('/', methods=['get'])
def index():
    return render_template('index.html', name="Index")


@router.route('/welcome', methods=['get'])
def main():
    return render_template('welcome.html', name="Welcome")


@router.route('/uploadRDF', methods=['get'])
def upload():
    return render_template('rdfUpload.html', name="Upload")


@router.route('/uploadHistory', methods=['get'])
def uploadHistory():
    db_interface = current_app.config['DB_INTERFACE']
    allRecords = db_interface.get_all_records()
    return render_template('uploadHistory.html', name="History", records=allRecords)


@router.route('/about', methods=['get'])
def about():
    return render_template('about.html', name="About")


@router.route('/sparQL', methods=['get'])
def sparQL():
    return render_template('sparQL.html', name="sparQL")


@router.route('/detail/<subpath>', methods=['get'])
def detail(subpath):
    db_interface = current_app.config['DB_INTERFACE']
    data = db_interface.get_upload_record(subpath)
    if data is None:
        return redirect(url_for('router.uploadHistory'))
    jenaClient = current_app.config['JENA_CLIENT']
    rdf_data = jenaClient.get_rdf_data_for_graph(subpath)
    # print(rdf_data)
    # print(data)
    return render_template('detail.html', name="Detail", insert_id=subpath, record=data, rdf_data=rdf_data)
