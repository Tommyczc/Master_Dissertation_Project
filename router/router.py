from flask import render_template, Blueprint

router = Blueprint('router', __name__)


@router.route('/', methods=['get'])
def index():
    return render_template('index.html', name="Index")


@router.route('/welcome', methods=['get'])
def main():
    return render_template('welcome.html', name="Welcome")


@router.route('/uploadRDF', methods=['get'])
def upload():
    return render_template('rdf_upload.html', name="Upload")


@router.route('/about', methods=['get'])
def about():
    return render_template('about.html', name="About")
