from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from utils.bd import Database
from config import USER_COLLECTION
from datetime import datetime, timedelta

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.fname = user_data.get('fname')
        self.lname = user_data.get('lname')
        self.dob = user_data.get('dob')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password')
        self.role = user_data.get('role', 'user')
        self.profile_image = user_data.get('profile_image', '/static/uploads/profiles/default.png')

    @staticmethod
    def get_by_email(email):
        db = Database.get_instance()
        user_data = db[USER_COLLECTION].find_one({"email": email})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_by_id(user_id):
        from bson.objectid import ObjectId
        db = Database.get_instance()
        try:
            user_data = db[USER_COLLECTION].find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            return None
        return None

    @staticmethod
    def create_user(fname,lname,dob, email, password, role='user'):
        db = Database.get_instance()
        if db[USER_COLLECTION].find_one({"email": email}):
            return False 

        hashed_password = generate_password_hash(password)
        new_user = {
            "fname": fname,
            "lname" : lname,
            "dob" : dob,
            "email": email,
            "password": hashed_password,
            "role": role
        }
        db[USER_COLLECTION].insert_one(new_user)
        return True

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def update_password(email, new_password):
        db = Database.get_instance()
        hashed_password = generate_password_hash(new_password)
        result = db[USER_COLLECTION].update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )
        return result.modified_count > 0

    # --- OTP Functions ---

    @staticmethod
    def set_otp(email, otp):
        """Saving an OTP and a one-minute expiration time"""
        db = Database.get_instance()
        
        expiry_time = datetime.now() + timedelta(minutes=1) 
        
        db[USER_COLLECTION].update_one(
            {"email": email},
            {"$set": {"reset_otp": otp, "otp_expiry": expiry_time}}
        )

    @staticmethod
    def verify_otp(email, otp):
        """Checking the OTP and time"""
        db = Database.get_instance()
        user_data = db[USER_COLLECTION].find_one({"email": email})
        
        if not user_data:
            return False, "User not found"

        saved_otp = user_data.get('reset_otp')
        expiry = user_data.get('otp_expiry')

        if saved_otp != otp:
            return False, "Invalid OTP code"

        if datetime.now() > expiry:
            return False, "OTP has expired (1 minute limit)"

        return True, "Success"

    @staticmethod
    def reset_password_with_otp(email, new_password):
        """Enter a new password and delete the OTP"""
        db = Database.get_instance()
        hashed_password = generate_password_hash(new_password)
        
        db[USER_COLLECTION].update_one(
            {"email": email},
            {
                "$set": {"password": hashed_password},
                "$unset": {"reset_otp": "", "otp_expiry": ""}
            }
        )