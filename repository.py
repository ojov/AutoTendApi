from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker
from models import User, Meeting, Attendance

class AttendanceManager:
    def __init__(self, path="sqlite:///attendance.db", logging=False):
        self.engine = create_engine(path, echo=logging)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def user_exists(self, email):
        return self.session.query(User).filter(User.email == email).count() > 0

    def add_user(self, email, firstname, lastname, gender, password):
        user = User(
            email=email,
            firstname=firstname,
            lastname=lastname,
            gender=gender,
            # pin=pin,
            # organization=organization,
            password=password
        )
        self.session.add(user)
        self.session.commit()
        return "Account created successfully"

    def add_attendance(self, meeting_id, user_id, status):
        attendance = Attendance(
            meeting_id=meeting_id,
            user_id=user_id,
            status=status
        )
        self.session.add(attendance)
        self.session.commit()
        
    def check_user_exists(email, username):
    # Use the query object to check if user with the given email or username exists
        user = User.query.filter((User.email == email) | (User.username == username)).first()
        return bool(user)

    def get_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return None
        return {
            'id': user.id, 'email': user.email, 'firstname': user.firstname, 'lastname': user.lastname, 'username': user.username, 'gender': user.gender, 'password': user.password, 'notification_enabled': user.notification_enabled, 'privacy_enabled': user.privacy_enabled, 'organisation': user.organisation
        }

    def get_user_by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_attendance_by_meeting_id(self, meeting_id):
        return self.session.query(Attendance).filter(Attendance.meeting_id == meeting_id).all()

    def update_user(self, user_id, new_firstname, new_lastname, new_username, new_gender, new_privacy_enabled, new_notification_enabled, new_pin, new_organization, new_password):
        user = self.session.query(User).filter(User.id == user_id).first()
        if user:
            user.firstname = new_firstname
            user.lastname = new_lastname
            user.username = new_username
            user.gender = new_gender
            user.privacy_enabled = new_privacy_enabled
            user.notification_enabled = new_notification_enabled
            user.pin = new_pin
            user.organization = new_organization
            user.password = new_password
            self.session.commit()
            return "User updated successfully"
        else:
            return "User not found"

    def delete_user(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        if user:
            self.session.delete(user)
            self.session.commit()
            return "User deleted successfully"
        else:
            return "User not found"

    def delete_attendance(self, attendance_id):
        attendance = self.session.query(Attendance).filter(Attendance.id == attendance_id).first()
        if attendance:
            self.session.delete(attendance)
            self.session.commit()
            return "Attendance deleted successfully"
        else:
            return "Attendance not found"

    def get_users(self):
        return self.session.query(User).all()

    def search_attendance_by_user(self, user_id):
        return self.session.query(Attendance).filter(Attendance.user_id == user_id).all()

    def search_attendance_by_status(self, status):
        return self.session.query(Attendance).filter(Attendance.status == status).all()
