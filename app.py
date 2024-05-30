from flask import Flask, render_template, request, g, session, url_for, redirect, flash, send_from_directory, abort, jsonify
import os
import random
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import hashlib
from model import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000)
    return salt + password_hash

def check_password(password, password_hash):
    salt = password_hash[:16]
    stored_password_hash = password_hash[16:]
    new_password_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000)
    return new_password_hash == stored_password_hash


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return None
    return {
        'id': user.id, 'email': user.email, 'firstname': user.firstname, 'lastname': user.lastname, 'username': user.username, 'gender': user.gender, 'password': user.password, 'notification_enabled': user.notification_enabled, 'privacy_enabled': user.privacy_enabled, 'organization': user.organization, 'department': user.department
    }


@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is not None:
        g.user = get_user(user_id)
    else:
        g.user = None

def check_user_exists(email, username):
    # Use the query object to check if user with the given email or username exists
    user = User.query.filter((User.email == email) | (User.username == username)).first()
    return bool(user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = secure_filename(request.form['username'])
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        firstname = request.form['fname']
        lastname = request.form['lname']
        organization = request.form['organization']
        department = request.form['department']
        session['username'] = username

        if check_user_exists(email, username):
            error_message = 'User with the same email or username already exists.'
            return render_template('signup.html', error=error_message)
        
        elif password != confirmpassword:
            error_message = 'Passwords do not match.'
            return render_template('signup.html', error=error_message)

        password_hash = hash_password(password)
        user = User(email=email, username=username, password=password_hash, firstname=firstname, lastname=lastname, organization=organization, department=department)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

        session['username'] = username
        password_hash = user.password
        if check_password(password, password_hash):
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if g.user is None:
        return redirect(url_for('login'))
    
    user = session.get('username')
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
