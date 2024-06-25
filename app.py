from flask import Flask
from router.router import router
app = Flask(__name__)
app.register_blueprint(router)

# @app.route('/')
# def hello_world():  # put application's code here
#     return 'index'


if __name__ == '__main__':
    app.run()
