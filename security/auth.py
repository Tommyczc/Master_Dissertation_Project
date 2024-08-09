from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, LoginManager
from flask_login import current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signIn', methods=['GET', 'POST'])
def signIn():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = current_app.config['DB_INTERFACE'].find_by_username(username)
        # print('pass',user.password)
        # print('username',user.username)
        if user and user.password == password:
            print(f"User Login:\nusername: {user.username}")
            login_user(user)
            return jsonify("login success"),200
        else:
            return jsonify("Invalid username or password"), 403
    return render_template('signIn.html')


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    print(f"User Logout: \nusername: {current_user.username}")
    logout_user()
    return jsonify("Logout success"), 200


@auth_bp.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if current_app.config['DB_INTERFACE'].find_by_username(username) is None:
            # roles = request.form.getlist('roles')
            # hashed_password = generate_password_hash(password)
            current_app.config['DB_INTERFACE'].create_user(username, password)

            return jsonify("sign up success"),200
        else:
            return jsonify("Username already taken"), 403
    return render_template('signUp.html')
