from flask import Flask, render_template, request, g, session, url_for, redirect, flash, send_from_directory, abort, jsonify
import os
import random
from repository import *
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import qrcode
from services import *

import secrets
if not os.path.exists('static/qr_codes'):
    os.makedirs('static/qr_codes')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)

db = AttendanceManager()

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

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
        
        user = db.get_user_by_email(email)
        if not user:
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

        session['email'] = email
        password_hash = user.password
        if check_password(password, password_hash):
            session['user_id'] = user.id
            session['name']= user.firstname + " " + user.lastname
            return redirect('/dashboard')
        else:
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/create_meeting', methods=['POST'])
def create_meeting():
        meeting_id = secrets.token_urlsafe(4)
        title = request.form.get('title')
        url = "https://autotend-aqre.onrender.com/mark_attendance"
        
        if not meeting_id or not title:
            return render_template('start_meeting.html', error="Meeting ID and Title are required")
        
        # Generate the QR code
        qr_data = f"{title}-{meeting_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Save QR code image
        qr_code_filename = f"qr_code_{meeting_id}.png"
        img_path = os.path.join('static', 'qr_codes', qr_code_filename)
        img.save(img_path)
        db.add_meeting(title, meeting_id, session["user_id"])

        # Render the display QR code template
        return render_template('show_qr.html', meeting_id=meeting_id, title=title, qr_code_url=url_for('static', filename=f'qr_codes/{qr_code_filename}'))
    

@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'POST':
        if request.is_json:
            attendee_name = session["name"]
            data = request.get_json()
            meeting_code = data.get('lectureCode')
        else:
            firstname = request.form['first_name']
            lastname = request.form['last_name']
            attendee_name= firstname + " " + lastname
            meeting_code = request.form['meeting_code']
            attendee_id = 0
        # qr_code = request.form.get('qr_code')
        


        if not meeting_code or not attendee_name:
            return 'Meeting Code and attendee name are required'
        
        meeting = db.get_meeting_by_meet_code(meeting_code)

        if not meeting:
            return 'Meeting not found'
        attendee_id=session["user_id"]

        db.add_attendance(attendee_id, meeting.id, attendee_name, status='Present')
        
        return f'You have been marked present for {meeting.title}'
    return render_template('attendance-form.html')


@app.route('/signout')
def signout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

   
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
