from app import db, login_manager
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Time
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

# Set the login view for the login manager
login_manager.login_view = 'main.login'

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    euid = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # Hash the password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check hashed password
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Appointment Model
class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.String(200), nullable=False)

    # Relationship with User
    user = db.relationship('User', backref='appointments', lazy=True)

    def __repr__(self):
        return f'<Appointment {self.id} for user {self.user_id}>'

# Medication Model
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

    # Relationship with User
    user = relationship('User', backref='medications', lazy=True)

    def __repr__(self):
        return f'<Medication {self.medication_name}>'

# Emergency Contact Model
class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contact'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    relationship = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship with User
    user = db.relationship('User', backref='emergency_contacts', lazy=True)

    def __repr__(self):
        return f'<EmergencyContact {self.name}>'

# Questionnaire Model
class Questionnaire(db.Model):
    __tablename__ = 'questionnaire'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    happiness = db.Column(db.String(255), nullable=False)
    stress = db.Column(db.String(255), nullable=False)
    sleep = db.Column(db.String(255), nullable=False)
    energy = db.Column(db.String(255), nullable=False)
    support = db.Column(db.String(255), nullable=False)
    self_esteem = db.Column(db.String(255), nullable=False)
    anxiety = db.Column(db.String(255), nullable=False)
    interest = db.Column(db.String(255), nullable=False)
    concentration = db.Column(db.String(255), nullable=False)
    substance_use = db.Column(db.String(255), nullable=False)

    # Relationship with User
    user = db.relationship('User', backref='questionnaires', lazy=True)

    def __repr__(self):
        return f'<Questionnaire {self.id}>'

# UserProfile Model
class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    aim = db.Column(db.String(255), nullable=True)
    passion = db.Column(db.String(255), nullable=True)

    # Relationship with User
    user = db.relationship('User', backref='profile', lazy=True)

    def __repr__(self):
        return f'<UserProfile {self.id}>'
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover_image = db.Column(db.String(200), nullable=False)
    download_link = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Video {self.video_id}>'
    
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Assuming you want to relate predictions to users
    emotion = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction {self.emotion}>'
    
class Intervention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the user
    intervention_type = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Intervention {self.intervention_type} for User {self.user_id}>'    
