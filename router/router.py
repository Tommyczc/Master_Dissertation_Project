from flask import Flask, render_template,Blueprint
router = Blueprint('router', __name__)

@router.route('/')
def index():
    return render_template('index.html',name="index")

@router.route('/upload')
def upload():
    return render_template('rdf_upload.html',name="upload")