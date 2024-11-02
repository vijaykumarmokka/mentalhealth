from app import db, login_manager
from datetime import datetime 
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
login_manager.login_view = 'main.login'
from sqlalchemy.orm import relationship

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    euid = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)  # Removed decode

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.Time, nullable=False)  # Add the time column
    description = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Appointment {self.id} for user {self.user_id}>'

class Medication(db.Model):
    __tablename__ = 'medications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    medication_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=db.func.current_timestamp())

    # Establishing a relationship to User
    user = relationship("User", backref="medications")

    def __repr__(self):
        return f'<Medication {self.medication_name}>'

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    relationship = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Assuming you have a User model

    user = db.relationship('User', backref='emergency_contacts')
    
class UserProfile(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    aim = db.Column(db.String(255), nullable=True)
    passion = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref='profile', lazy=True)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Ensure this exists
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Integer, nullable=False)
    sleep_quality = db.Column(db.Integer, nullable=False)
    physical_activity = db.Column(db.Integer, nullable=False)
    diet_quality = db.Column(db.Integer, nullable=False)
    social_support = db.Column(db.Integer, nullable=False)
    relationship_status = db.Column(db.Integer, nullable=False)
    substance_use = db.Column(db.Integer, nullable=False)
    counseling_service_use = db.Column(db.Integer, nullable=False)
    family_history = db.Column(db.Integer, nullable=False)
    chronic_illness = db.Column(db.Integer, nullable=False)
    extracurricular_involvement = db.Column(db.Integer, nullable=False)
    residence_type = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)  # Make sure this is Float
    stress_level = db.Column(db.Integer, nullable=False)
    financial_stress = db.Column(db.Integer, nullable=False)
    semester_credit_load = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Assessment {self.id}>'
    
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
