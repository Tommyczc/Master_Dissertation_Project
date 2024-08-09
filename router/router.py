from flask import render_template, Blueprint, current_app, redirect, url_for
from flask_login import login_required

router = Blueprint('router', __name__)


@router.route('/', methods=['get'])
def index():
    return render_template('index.html', name="Index")


@router.route('/welcome', methods=['get'])
def main():
    return render_template('welcome.html', name="Welcome")


@router.route('/uploadRDF', methods=['get'])
@login_required
def upload():
    return render_template('rdfUpload.html', name="Upload")


@router.route('/uploadHistory', methods=['get'])
def uploadHistory():
    db_interface = current_app.config['DB_INTERFACE']
    allRecords = db_interface.get_all_records()
    # print(allRecords)
    return render_template('uploadHistory.html', name="History", records=allRecords)


@router.route('/about', methods=['get'])
def about():
    return render_template('about.html', name="About")


@router.route('/sparQL', methods=['get'])
def sparQL():
    return render_template('sparQL.html', name="sparQL")


@router.route('/QASystem', methods=['get'])
def QASystem():
    return render_template('QA_System.html', name="Question & Answering")


@router.route('/detail/<subpath>', methods=['get'])
def detail(subpath):
    db_interface = current_app.config['DB_INTERFACE']
    data = db_interface.get_upload_record(subpath)
    if data is None:
        return redirect(url_for('router.uploadHistory'))
    return render_template('detail.html', name="Detail", insert_id=subpath, record=data)
