from flask import Flask, render_template, request, g, session, url_for, redirect, flash, send_from_directory, abort, jsonify
import os
import random
from repository import *
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import hashlib


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = AttendanceManager()
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



@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is not None:
        g.user = db.get_user(user_id)
    else:
        g.user = None


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = secure_filename(request.form['username'])
        password = request.form['password']
        gender = request.form['gender']
        lastname = request.form['lastname']
        session['username'] = username

        if db.check_user_exists(email, username):
            error_message = 'User with the same email or username already exists.'
            return render_template('signup.html', error=error_message)

        password_hash = hash_password(password)
        user = User( firstname=username, lastname=lastname, gender=gender,email=email, password=password_hash)
        db.add_user(user)
        
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.get_user_by_email(username)
        if not user:
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

        password_hash = user.password
        if check_password(password, password_hash):
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/create_meeting', methods=['POST'])
def create_meeting():
    title = request.form.get('title')
    
    if not title:
        return 'Title is required'
    
    # Generate a QR code
    qr_code = secrets.token_urlsafe(16)

    new_meeting = Meeting(title=title, qr_code=qr_code)
    db.session.add(new_meeting)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    qr_code = request.form.get('qr_code')
    attendee_name = request.form.get('attendee_name')

    if not qr_code or not attendee_name:
        return 'QR code and attendee name are required'
    
    meeting = Meeting.query.filter_by(qr_code=qr_code).first()

    if not meeting:
        return 'Meeting not found'

    new_attendance = Attendance(meeting_id=meeting.id, attendee_name=attendee_name, is_present=True)
    db.session.add(new_attendance)
    db.session.commit()
    return 'Attendance marked successfully'


@app.route('/signout')
def signout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

   
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if g.user is None:
        return redirect(url_for('login'))
    
    current_user = User.query.get(g.user['id'])
    return render_template('dashboard.html', user=current_user)

if __name__ == '__main__':
    app.run()
