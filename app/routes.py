from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
import requests
from flask_socketio import SocketIO, emit
from datetime import datetime
from app.models import User,Appointment,Book,Video,Prediction
from app.models import db, EmergencyContact,UserProfile,Medication,Intervention
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired



main = Blueprint('main', __name__)
socketio = SocketIO()



@main.route("/")    
def home():
    return render_template('home.html')



@main.route("/game")
@login_required
def game():
    return render_template('game.html')



@main.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST':
    
        if 'cancel' in request.form:
            return redirect(url_for('main.home'))

        if form.validate_on_submit():
            
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('Email is already taken. Please use a different email.', 'danger')
                return redirect(url_for('main.register'))

            
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(euid=form.euid.data, first_name=form.first_name.data,
                        last_name=form.last_name.data, dob=form.dob.data,
                        email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Please correct the errors in the form.', 'danger')

    return render_template('register.html', form=form)



@main.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            
            if user.email=="admin@gmail.com" :
                return redirect(url_for('main.admin_index'))
            elif user.euid=="professional":
                return redirect(url_for('main.doctorindex'))
            else:
                return redirect(url_for('main.game'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)
@main.route('/admin')
@login_required
def admin_index():
    pro = User.query.all()
    return render_template('admin_index.html',pro=pro)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@main.route("/index")
@login_required
def index():
    return render_template('index.html')

@main.route("/about")
def about():
    return render_template('about.html')



from app.models import Questionnaire  



@main.route('/questionarie', methods=['GET', 'POST'])
@login_required
def submit_questionnaire():
     if not current_user.is_authenticated:
        flash('You need to be logged in to submit a questionnaire.', 'warning')
        return redirect(url_for('main.login'))
      # Renamed the function to avoid conflict
     elif request.method == 'POST':
        # Create a new questionnaire instance with form data
        new_questionnaire = Questionnaire(
            user_id=current_user.id,
            happiness=request.form.get('happiness'),  # Use get to avoid KeyError if the field is missing
            stress=request.form.get('stress'),
            sleep=request.form.get('sleep'),
            energy=request.form.get('energy'),
            support=request.form.get('support'),
            self_esteem=request.form.get('self-esteem'),
            anxiety=request.form.get('anxiety'),
            interest=request.form.get('interest'),
            concentration=request.form.get('concentration'),
            substance_use=request.form.get('substance_use')
        )

        # Add the new questionnaire to the session and commit to the database
        db.session.add(new_questionnaire)
        db.session.commit()

        flash('Assessment submitted successfully!', 'success')
        return redirect(url_for('main.index')) 

     return render_template('questionarie.html')  # Render the form for GET requests

import pickle
from .models import Questionnaire

# Load model and vectorizer at the top-level to avoid reloading them for every request
with open('./model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

with open('./vectorizer.pkl', 'rb') as file:
    loaded_vectorizer = pickle.load(file)

# Define a function for text cleaning (if needed)
def clean_text(text):
    # Your cleaning logic here (e.g., lowercasing, removing punctuation)
    return text.lower()  # Example cleaning step, expand as needed

@main.route('/predict_emotion',methods=['GET','POST'])
def predict_emotion():
    # Retrieve and concatenate the latest assessments
    latest_results = (
    Questionnaire.query
    .filter_by(user_id=current_user.id)  # Filter by the current user's ID
    .order_by(Questionnaire.id.desc())
    .limit(1)
    .all()
)
    concatenated_result = ""
    for result in latest_results:
        concatenated_result += (
            f"Happiness: {result.happiness}, "
            f"Stress: {result.stress}, "
            f"Sleep: {result.sleep}, "
            f"Energy: {result.energy}, "
            f"Support: {result.support}, "
            f"Self-Esteem: {result.self_esteem}, "
            f"Anxiety: {result.anxiety}, "
            f"Interest: {result.interest}, "
            f"Concentration: {result.concentration}, "
            f"Substance Use: {result.substance_use}. "
        )
    print(concatenated_result)
    # Clean and transform concatenated text
    if concatenated_result=="":
            return render_template('predicted_emotion.html', emotion="give assessment first")
    
    new_text_cleaned = [clean_text(concatenated_result)]
    new_text_tfidf = loaded_vectorizer.transform(new_text_cleaned)

    predicted_emotion = loaded_model.predict(new_text_tfidf)

    # Render result in a template or return as a response
    user_id = current_user.id  # Assumes user is logged in and current_user is accessible
    new_prediction = Prediction(user_id=user_id, emotion=predicted_emotion)
    db.session.add(new_prediction)
    db.session.commit()
    return render_template('predicted_emotion.html', emotion=predicted_emotion[0])

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/view_intervention', methods=['GET'])
@login_required
def view_intervention():
    # Fetch interventions for the logged-in user
    interventions = Intervention.query.filter_by(user_id=current_user.id).all()
    # Render the interventions page with the user's interventions
    return render_template('view_intervention.html', interventions=interventions, user=current_user)
  

@main.route('/uploadbook', methods=['GET', 'POST'])
def upload_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        cover_image = request.form.get('cover_image')
        download_link = request.form.get('download_link')

        new_book = Book(title=title, author=author, cover_image=cover_image, download_link=download_link)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('main.upload_book'))
    return render_template('upload_book.html')

@main.route('/uploadvideo', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        video_id = request.form.get('video_id')

        new_video = Video(video_id=video_id)
        db.session.add(new_video)
        db.session.commit()

        return redirect(url_for('main.upload_video'))
    return render_template('upload_video.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

@main.route("/educational_resources")
@login_required
def educational_resources():
    print("Educational resources route accessed")  
    return render_template('educational_resources')


        
@main.route('/appointments/schedule', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    if request.method == 'POST':
        date_str = request.form.get('date') 
        time_str = request.form.get('time')  
        description = request.form.get('description')

        if not date_str or not time_str:
            flash('Date and Time are required.', 'danger')
            return render_template('schedule_appointment.html')

        try:

            date = datetime.fromisoformat(date_str)
            time = datetime.strptime(time_str, '%H:%M').time()  

        
            new_appointment = Appointment(
                user_id=1,  
                date=date,
                time=time,  
                description=description
            )

            db.session.add(new_appointment)
            db.session.commit()
            flash('Appointment scheduled successfully!', 'success')
            return redirect(url_for('main.appointments'))

        except Exception as e:
            flash(f"Error scheduling appointment: {str(e)}", 'danger')
            return render_template('schedule_appointment.html')

    return render_template('schedule_appointment.html')

@main.route('/appointments/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        appointment.date = datetime.fromisoformat(request.form['date'])  
        appointment.description = request.form['description']
        db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('main.appointments'))

    return render_template('edit_appointment.html', appointment=appointment)

@main.route('/appointments/delete/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('main.appointments'))

@main.route('/appointments', methods=['GET'])
@login_required
def appointments():
    all_appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=all_appointments)


@main.route('/track_medications', methods=['GET', 'POST'])
@login_required
def track_medications():
    if request.method == 'POST':
        medication_name = request.form['medication_name']
        dosage = request.form['dosage']
        frequency = request.form['frequency']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        notes = request.form['notes']

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()  # Convert to date object
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None  # Handle optional end date

        new_medication = Medication(
            user_id=current_user.id,  
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            notes=notes
        )

        try:
            db.session.add(new_medication)
            db.session.commit()
            flash('Medication added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding medication: {e}', 'danger')

        return redirect(url_for('main.track_medications'))

    medications = Medication.query.filter_by(user_id=current_user.id).all()
    return render_template('track_medications.html', medications=medications)
@main.route('/edit_medication/<int:medication_id>', methods=['GET', 'POST'])
@login_required
def edit_medication(medication_id):
    medication = Medication.query.get_or_404(medication_id)

    if request.method == 'POST':
        medication.medication_name = request.form['medication_name']
        medication.dosage = request.form['dosage']
        medication.frequency = request.form['frequency']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        medication.notes = request.form['notes']

        medication.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        medication.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        try:
            db.session.commit()
            flash('Medication updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating medication: {e}', 'danger')

        return redirect(url_for('main.track_medications'))

    return render_template('edit_medication.html', medication=medication)

@main.route('/delete_medication/<int:medication_id>', methods=['POST'])
@login_required
def delete_medication(medication_id):
    medication = Medication.query.get_or_404(medication_id)

    try:
        db.session.delete(medication)
        db.session.commit()
        flash('Medication deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting medication: {e}', 'danger')

    return redirect(url_for('main.track_medications'))






from app.models import EmergencyContact  
    
@main.route('/emergency_support', methods=['GET', 'POST'])
@login_required  
def emergency_support():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        relationship = request.form['relationship']
        
        if not current_user.is_authenticated:
            flash('You need to be logged in to add contacts.', 'danger')
            return redirect(url_for('auth.login'))  

        new_contact = EmergencyContact(
            name=name,
            phone=phone,
            relationship=relationship,
            user_id=current_user.id  
        )
        
        try:
            db.session.add(new_contact)
            db.session.commit()
            flash('Emergency contact added successfully!', 'success')
        except Exception as e:
            db.session.rollback()  
            flash(f'Error adding contact: {str(e)}', 'danger')
        
        return redirect(url_for('main.emergency_support'))

    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    return render_template('emergency_support.html', contacts=contacts)



    contacts = EmergencyContact.query.all()  
    emergency_numbers = [...]  
    return render_template('emergency_support.html', contacts=contacts, emergency_numbers=emergency_numbers)
@main.route("/edit_contact/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    contact = EmergencyContact.query.get_or_404(id)

    if request.method == 'POST':
        contact.name = request.form['name']
        contact.phone = request.form['phone']
        contact.relationship = request.form['relationship']

        try:
            db.session.commit()
            flash('Contact updated successfully!', 'success')
            return redirect(url_for('main.emergency_support'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating contact: {e}', 'danger')

    return render_template('edit_contact.html', contact=contact)

@main.route("/delete_contact/<int:id>", methods=["POST"])
@login_required
def delete_contact(id):
    contact = EmergencyContact.query.get(id)
    if contact and contact.user_id == current_user.id:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact has been deleted!', 'success')
    else:
        flash('Contact not found or you do not have permission to delete this contact.', 'danger')
    return redirect(url_for('main.emergency_support'))



from app.models import UserProfile

@main.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        if not profile:
            profile = UserProfile(user_id=current_user.id)
        profile.address = request.form.get('address') or None
        profile.phone_number = request.form.get('phone_number') or None
        profile.occupation = request.form.get('occupation') or None
        profile.aim = request.form.get('aim') or None
        profile.passion = request.form.get('passion') or None

        try:
            db.session.add(profile)
            db.session.commit()
            flash('Profile saved successfully', 'success')
            return redirect(url_for('main.display_user_profile'))

        except Exception as e:
            flash(f'Error saving profile: {str(e)}', 'danger')

    return render_template('user_profile.html', profile=profile)

@main.route('/display_user_profile', methods=['GET'])
@login_required
def display_user_profile():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('No profile found. Please create your profile first.', 'info')
        return redirect(url_for('main.user_profile'))

    return render_template('display_user_profile.html', profile=profile)


@main.route('/books')
def books():
    all_books = Book.query.all()  # Fetch all books from the database
    return render_template('books.html', books=all_books)

@main.route('/videos')
def videos():
    videos = Video.query.all()  # Fetch all video records
    return render_template('videos.html', videos=videos)

@main.route('/doctor')
def doctor():
    # Query users with EUID set to "PROFESSIONAL"
    professionals = User.query.filter_by(euid="professional").all()
    return render_template('doctor.html', professionals=professionals)

@main.route('/doctorindex')
def doctorindex():
    # Query users with EUID set to "PROFESSIONAL"
    persons = User.query.filter_by(euid="regular").all()
    return render_template('doctorindex.html', persons=persons)

@main.route('/prediction_history/<int:user_id>')
@login_required
def prediction_history(user_id):
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.timestamp.desc()).all()
    return render_template('prediction_history.html', predictions=predictions)


@main.route('/view_user_profile/<int:user_id>')
@login_required
def view_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    assessments = Questionnaire.query.filter_by(user_id=user_id).all()
    appointments = Appointment.query.filter_by(user_id=user_id).all()
    medications = Medication.query.filter_by(user_id=user_id).all()
    predicted_results = Prediction.query.filter_by(user_id=user_id).all()
    interventions = Intervention.query.filter_by(user_id=user_id).all()

    return render_template(
        'view_user_profile.html',
        user=user,
        user_profile=user_profile,
        assessments=assessments,
        appointments=appointments,
        medications=medications,
        predicted_results=predicted_results,
        interventions=interventions
    )

from app.models import User, Intervention
from app.forms import InterventionForm

@main.route('/add_intervention/<int:user_id>', methods=['GET', 'POST'])
@login_required
def add_intervention(user_id):
    user = User.query.get_or_404(user_id)
    form = InterventionForm()
    if form.validate_on_submit():
        intervention = Intervention(
            user_id=user.id,
            intervention_type=form.intervention_type.data,
            details=form.details.data
        )
        db.session.add(intervention)
        db.session.commit()
        flash('Intervention added successfully!', 'success')
        return redirect(url_for('main.view_user_profile', user_id=user.id))  # Use the correct profile view
    return render_template('add_intervention.html', form=form, user=user)


from flask import session
@main.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)


 