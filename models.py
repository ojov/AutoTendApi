import sqlite3, random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Integer, Column, ForeignKey, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime


# Initializing an instance of the SQLAlchemy class
Base = db.

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    username = Column(String(50))
    email = Column(String(50), unique=True)
    organization = String(100)
    gender = Column(String(50))
    password = Column(String(64))
    
class Meeting(Base):
    __tablename__ = 'meetings'
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    admin = relationship('User', back_populates='meetings')
    title = Column(String(100), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    qr_code_id = Column(Integer, ForeignKey('qr_code.id'))
    qr_code = relationship('QRCode', back_populates='meeting')
    attendances = relationship('Attendance', back_populates='meeting')

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    meeting = relationship('Meeting', back_populates='attendances')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='attendances')
    attendance_time = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('Present', 'Absent', 'Late', name='attendance_status'), default='Present')

class QRCode(Base):
    __tablename__ = 'qr_code'
    id = Column(Integer, primary_key=True)
    qr_code_data = Column(Text, nullable=False)
    generated_time = Column(DateTime, default=datetime.utcnow)
    meeting = relationship('Meeting', back_populates='qr_code')