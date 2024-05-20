#!/usr/bin/env python3
import subprocess
from flask import Flask, request, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
app.config['JWT_SECRET_KEY'] = '123'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_HTTPONLY'] = False

# Disable HttpOnly for session cookies
app.config['SESSION_COOKIE_HTTPONLY'] = False

login_manager = LoginManager()
login_manager.init_app(app)

jwt = JWTManager(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

admin_user = User(id='admin')
admin_password = 'admin'

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return admin_user
    return None

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         if username == admin_user.id and password == admin_password:
#             login_user(admin_user)
#             access_token = create_access_token(identity={'username': username})
#             response = redirect(url_for('index'))
#             response.set_cookie('access_token_cookie', access_token, max_age=datetime.timedelta(days=1), httponly=False)
#             session['access_token'] = access_token  # Add token to session without HttpOnly
#             return response
#         return 'Invalid credentials', 401
#     return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    response = redirect(url_for('index'))
    response.delete_cookie('access_token_cookie')
    session.pop('access_token', None)
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == admin_user.id and password == admin_password:
            login_user(admin_user)
            access_token = create_access_token(identity={'username': username})
            response = redirect(url_for('index'))
            response.set_cookie('access_token_cookie', value=access_token, httponly=False)
            session['access_token'] = access_token
            return response
        return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/ping', methods=['GET', 'POST'])
@jwt_required()
def ping():
    try:
        current_identity = get_jwt_identity()
    except JWTError:
        return redirect(url_for('login'))

    if request.method == 'POST':
        host = request.form.get('host')
        cmd = f'ping -c 4 {host}'
        try:
            output = subprocess.check_output(['/bin/sh', '-c', cmd], timeout=5)
            return render_template('ping_result.html', data=output.decode('utf-8'))
        except subprocess.CalledProcessError:
            return render_template('ping_result.html', data=f'Error when executing command: {cmd}')

    return render_template('ping.html')
@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        results = f'Search results for "{query}"'
        return render_template('search_result.html', data=results)
    return render_template('search.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
