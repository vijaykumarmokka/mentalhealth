from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
import requests
from flask_socketio import SocketIO, emit
from datetime import datetime
from app.models import User,Appointment,ChatMessage
from app.models import db, EmergencyContact,UserProfile,Medication
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
import pickle
import pandas as pd
import matplotlib.pyplot as plt

main = Blueprint('main', __name__)
socketio = SocketIO()



@main.route("/")    
def home():
    return render_template('home.html')

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
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)


@main.route("/logout")
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


from app.models import Assessment

@main.route("/assesment", methods=['GET', 'POST'])
@login_required
def assesment():
    if request.method == 'POST':
        try:
            assessment = Assessment(
                user_id=current_user.id,
                course=int(request.form['Course']),
                gender=int(request.form['Gender']),
                sleep_quality=int(request.form['Sleep_Quality']),
                physical_activity=int(request.form['Physical_Activity']),
                diet_quality=int(request.form['Diet_Quality']),
                social_support=int(request.form['Social_Support']),
                relationship_status=int(request.form['Relationship_Status']),
                substance_use=int(request.form['Substance_Use']),
                counseling_service_use=int(request.form['Counseling_Service_Use']),
                family_history=int(request.form['Family_History']),
                chronic_illness=int(request.form['Chronic_Illness']),
                extracurricular_involvement=int(request.form['Extracurricular_Involvement']),
                residence_type=int(request.form['Residence_Type']),
                age=int(request.form['Age']),
                cgpa=float(request.form['CGPA']),
                stress_level=int(request.form['Stress_Level']),
                financial_stress=int(request.form['Financial_Stress']),
                semester_credit_load=int(request.form['Semester_Credit_Load'])
            )
            print(f'Creating Assessment: {assessment}')

    
            db.session.add(assessment)
            db.session.commit()
            flash("Assessment submitted successfully!", "success")
            return redirect(url_for('main.predict'))
        except Exception as e:
            db.session.rollback()  
            print(f"Error occurred: {e}")  
            flash(f"Error occurred while submitting the assessment: {e}", "danger")

    return render_template('assesment.html')












import io
import base64


@main.route("/charts")
def charts():
    assessments = Assessment.query.all()
    
    if not assessments:
        return render_template('charts.html', charts=None, message="No assessment data found. Please take the assessment.")

    data = pd.DataFrame([{
        "Course": a.course,
        "Gender": a.gender,
        "Sleep Quality": a.sleep_quality,
        "Physical Activity": a.physical_activity,
        "Diet Quality": a.diet_quality,
        "Social Support": a.social_support,
        "Relationship Status": a.relationship_status,
        "Substance Use": a.substance_use,
        "Counseling Service Use": a.counseling_service_use,
        "Family History": a.family_history,
        "Chronic Illness": a.chronic_illness,
        "Extracurricular Involvement": a.extracurricular_involvement,
        "Residence Type": a.residence_type,
        "Age": a.age,
        "CGPA": a.cgpa,
        "Stress Level": a.stress_level,
        "Financial Stress": a.financial_stress,
        "Semester Credit Load": a.semester_credit_load
    } for a in assessments])

    charts_base64 = {}


    features_for_bar_chart = [
        'Sleep Quality',
        'Physical Activity',
        'Diet Quality',
        'Social Support',
        'Relationship Status',
        'Substance Use',
        'Counseling Service Use',
        'Family History',
        'Chronic Illness',
        'Extracurricular Involvement',
        'Residence Type',
        'Stress Level',
        'Financial Stress'
    ]

    feature_counts = data[features_for_bar_chart].apply(pd.Series.value_counts).fillna(0)
    feature_counts = feature_counts.sum().sort_index()

    plt.figure(figsize=(10, 6))
    feature_counts.plot(kind='bar', color='skyblue')
    plt.title('Frequency of Selected Features')
    plt.xlabel('Features')
    plt.ylabel('Frequency')

    bar_chart = io.BytesIO()
    plt.savefig(bar_chart, format='png')
    bar_chart.seek(0)
    charts_base64['Feature Frequency'] = base64.b64encode(bar_chart.getvalue()).decode('utf-8')
    plt.close()  


    positive_features = [
        'Physical Activity',
        'Social Support',
        'Diet Quality',
        'Counseling Service Use',
        'Extracurricular Involvement'
    ]

    negative_features = [
        'Substance Use',
        'Chronic Illness',
        'Stress Level',
        'Financial Stress'
    ]
    positive_count = data[positive_features].notnull().sum().sum()
    negative_count = data[negative_features].notnull().sum().sum()


    pie_data = [positive_count, negative_count]
    pie_labels = ['Positive Impact', 'Negative Impact']

    plt.figure(figsize=(8, 8))
    plt.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#FF5722'])
    plt.title('Positive vs Negative Impact Features')
    
    pie_chart = io.BytesIO()
    plt.savefig(pie_chart, format='png')
    pie_chart.seek(0)
    charts_base64['Positive vs Negative Impact'] = base64.b64encode(pie_chart.getvalue()).decode('utf-8')
    plt.close()  

    return render_template('charts.html', charts=charts_base64)




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
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('main.appointments'))

@main.route('/appointments', methods=['GET'])
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


import os

base_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(base_dir, 'model.pkl')

with open(model_path, 'rb') as f:
    RF_model = pickle.load(f)

@main.route('/predict', methods=['GET'])
@login_required
def predict():
    user_id = current_user.id
    assessment = Assessment.query.filter_by(user_id=user_id).first()

    if not assessment:
        flash('No assessment data found for this user.', 'danger')
        return redirect(url_for('main.assesment'))  
    data_df = pd.DataFrame([{
        'Course': assessment.course,
        'Gender': assessment.gender,
        'Sleep_Quality': assessment.sleep_quality,
        'Physical_Activity': assessment.physical_activity,
        'Diet_Quality': assessment.diet_quality,
        'Social_Support': assessment.social_support,
        'Relationship_Status': assessment.relationship_status,
        'Substance_Use': assessment.substance_use,
        'Counseling_Service_Use': assessment.counseling_service_use,
        'Family_History': assessment.family_history,
        'Chronic_Illness': assessment.chronic_illness,
        'Extracurricular_Involvement': assessment.extracurricular_involvement,
        'Residence_Type': assessment.residence_type,
        'Age': assessment.age,
        'CGPA': assessment.cgpa,
        'Stress_Level': assessment.stress_level,
        'Financial_Stress': assessment.financial_stress,
        'Semester_Credit_Load': assessment.semester_credit_load
    }])

    predicted_value = RF_model.predict(data_df)[0]

    if predicted_value == 0:
        message = (
            "Prediction Value: 0 (No or Very Low Depression)\n\n"
            "Intervention & Insights: Congratulations on achieving a state of no or very low depression! This is a positive sign of your mental well-being. "
            "To maintain your mental health, consider adopting the following practices:\n\n"
            "Precautions: Continue engaging in regular physical activity, as it can help enhance your mood and overall well-being. "
            "Make sure to prioritize sufficient sleep and a balanced diet, as these factors significantly contribute to your mental health.\n\n"
            "Work to Do: Explore new hobbies or activities that interest you. Engaging in creative outlets such as art, music, or sports can provide a fulfilling way "
            "to express yourself and connect with others.\n\n"
            "Consulting a Doctor: While your current state is positive, it’s always beneficial to check in with a healthcare professional if you notice any changes "
            "in your mood or behavior. Regular mental health check-ups can provide support and ensure you continue to thrive."
        )
    elif predicted_value == 1:
        message = (
            "Prediction Value: 1 (Mild to Moderate Depression)\n\n"
            "Intervention & Insights: A prediction of mild to moderate depression indicates that it may be helpful for you to take proactive steps to improve your mental health.\n\n"
            "Precautions: Pay attention to your feelings and identify any triggers that contribute to your mood changes. "
            "Make an effort to engage in self-care activities that you enjoy and that bring you relaxation and joy.\n\n"
            "Work to Do: Consider setting small, achievable goals for yourself each day to instill a sense of accomplishment. "
            "This could include simple tasks like taking a walk, reading a book, or practicing mindfulness exercises. Keeping a journal to express your thoughts and feelings can also be beneficial.\n\n"
            "Consulting a Doctor: It’s important to consult a mental health professional who can provide guidance tailored to your situation. "
            "They can suggest therapies or coping strategies and may recommend counseling or medication if necessary. Don't hesitate to seek help—acknowledging your feelings is a crucial step toward healing."
        )
    elif predicted_value == 2:
        message = (
            "Prediction Value: 2 (Severe Depression)\n\n"
            "Intervention & Insights: A prediction of severe depression signals that you may be facing significant challenges that require immediate attention and support. "
            "It’s crucial to take this seriously and explore available resources:\n\n"
            "Precautions: Prioritize your safety and well-being. Remove any potential sources of harm and ensure you have a supportive environment around you. "
            "It’s important to reach out to trusted friends or family members and communicate how you’re feeling.\n\n"
            "Work to Do: Take small steps to manage your daily activities. Consider implementing a structured routine that includes basic self-care practices like eating, sleeping, "
            "and engaging in light physical activities, even if it feels difficult. Celebrate any small victories, as they can contribute to improving your mood over time.\n\n"
            "Consulting a Doctor: Seeking professional help is critical at this stage. A qualified mental health professional can provide a thorough assessment and recommend a treatment plan tailored to your needs. "
            "They may suggest psychotherapy, medication, or a combination of both. If you have thoughts of self-harm or are in crisis, please seek immediate help from emergency services or a crisis hotline."
        )
    else:
        message = "An unexpected error occurred. Please try again later."
    return render_template('result.html', interventions={"title": f"Depression Level: {predicted_value}", "message": message})









    
@main.route("/chat")
@login_required
def chat():
    return render_template('chat.html')

# Send a message
@socketio.on('send_message')
def handle_send_message(data):
    message = ChatMessage(
        sender_id=current_user.id,
        receiver_id=data['receiver_id'],
        content=data['content'],
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()

    emit('receive_message', {
        'sender_id': current_user.id,
        'content': data['content'],
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, room=data['receiver_id'])

# Get messages between users
@main.route("/messages/<int:receiver_id>")
@login_required
def get_messages(receiver_id):
    messages = ChatMessage.query.filter(
        (ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == receiver_id) |
        (ChatMessage.sender_id == receiver_id) & (ChatMessage.receiver_id == current_user.id)
    ).order_by(ChatMessage.timestamp).all()
    
    return render_template('messages.html', messages=messages, receiver_id=receiver_id)