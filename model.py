import sqlite3, random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Integer, Column, ForeignKey, String
from datetime import datetime

# Initializing an instance of the SQLAlchemy class
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=lambda: random.randint(1000000000, 9999999999))
    email = db.Column(db.String(50), unique=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)    
    gender = db.Column(db.String(50))
    privacy_enabled = db.Column(db.Boolean, default=False)
    notification_enabled = db.Column(db.Boolean, default=False)
    pin = db.Column(db.Integer)
    organization = db.String(100)
    department = db.String(100)
    password = db.Column(db.String(64))