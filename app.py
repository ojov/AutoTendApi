from flask import Flask, render_template, request, g, session, url_for, redirect, flash, send_from_directory, abort, jsonify
import os
import random
from repository import *
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from services import *

import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)

db = AttendanceManager()

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
        confirmpassword = request.form['confirmpassword']
        firstname = request.form['fname']
        lastname = request.form['lname']
        organization = request.form['organization']
        
        if password != confirmpassword:
            error_message = 'Passwords do not match.'
            return render_template('signup.html', error=error_message)
        session['username'] = username
        
        if db.check_user_exists(email, username):
            error_message = 'User with the same email or username already exists.'
            return render_template('signup.html', error=error_message)
        password_hash = hash_password(password)
        db.add_user(email, username, firstname, lastname, password_hash, organization)
        
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        breakpoint()
        user = db.get_user_by_email(email)
        if not user:
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

        session['email'] = email
        password_hash = user.password
        breakpoint()
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
    
    user = session.get('email')
    return render_template('dashboard.html', user=user)

@app.route('/tracker')
def tracker():
    if g.user is None:
        return redirect(url_for('login'))
    
    return render_template('trackATD.html')

@app.route('/create')
def create():
    if g.user is None:
        return redirect(url_for('login'))
    
    return render_template('createATD.html')

@app.route('/records')
def records():
    if g.user is None:
        return redirect(url_for('login'))
    
    return render_template('records.html')

@app.route('/markATD')
def markATD():
    if g.user is None:
        return redirect(url_for('login'))
    
    return render_template('markATD.html')

@app.route('/schedule')
def schedule():
    if g.user is None:
        return redirect(url_for('login'))
    
    return render_template('schedule.html')

@app.route('/summary')
def summary():
    if g.user is None:
        return redirect(url_for('login'))
    
    return render_template('summary.html')

if __name__ == '__main__':
    app.run(debug=True)
