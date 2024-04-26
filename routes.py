from flask import Blueprint, jsonify, request, abort
from datetime import datetime, timedelta
from models import Doctor, Appointment, Patient
from extensions import db
import re

bp = Blueprint("main", __name__)

'''
Method-GET
Sample URL: http://127.0.0.1:5000/doctors
Response on Success (Status 200): 
<List of doctors>
Description: Gets a list of doctors
'''
@bp.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    doctor_list = [{'id': doctor.id, 'first_name': doctor.first_name, 'last_name': doctor.last_name} for doctor in doctors]
    return jsonify(doctor_list)

'''
Method-GET
Params: doctor_id, date
Sample URL: http://127.0.0.1:5000/appointments/1/2024-04-27
Response on Success (Status 200): 
<List of appointments>
Description: Gets a list of appointments for a valid doctor_id and given date
'''
@bp.route('/appointments/<int:doctor_id>/<date>', methods=['GET'])
def get_appointments(doctor_id, date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Please use YYYY-MM-DD.")

    session = db.session
    doctor = session.query(Doctor).filter_by(id=doctor_id).first()
    if not doctor:
        abort(404, description="Doctor not found.")

    start_date = datetime.strptime(date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    appointments = session.query(Appointment).filter(Appointment.doctor_id == doctor_id, Appointment.date_time >= start_date, Appointment.date_time < end_date).all()
    appointment_list = []
    for appointment in appointments:
        patient = appointment.patient
        appointment_list.append({'id': appointment.id, 'patient_first_name': patient.first_name, 'patient_last_name': patient.last_name, 'email': patient.email, 'date_time': appointment.date_time.strftime('%Y-%m-%d %H:%M:%S'), 'kind': appointment.kind})
    return jsonify(appointment_list)

'''
Method-DELETE
Params: appointment_id
Sample URL: http://127.0.0.1:5000/appointments/1
Response on Success (Status 200): 
{
    "message": "Appointment deleted successfully"
}
Description: Deletes an appointment for a valid appointment_id
'''
@bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    session = db.session
    appointment = session.query(Appointment).get(appointment_id)
    if appointment:
        session.delete(appointment)
        session.commit()
        return jsonify({'message': 'Appointment deleted successfully'})
    else:
        abort(404, description="Appointment not found")

'''
Method-POST
JSON Body Request Example:
{
    "doctor_id": 1,
    "patient_first_name": "Ram",
    "patient_last_name": "Charan",
    "email": "abc@gmail.com",
    "date_time": "2024-04-27 10:15:00"
}
Response on Success (Status 200): 
{
    "message": "Appointment added successfully"
}
Description: Adds an appointment for the patient when valid parameters are given in the POST request JSON body
'''
@bp.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.json
    doctor_id = data.get('doctor_id')
    patient_first_name = data.get('patient_first_name')
    patient_last_name = data.get('patient_last_name')
    email = data.get('email')
    date_time_str = data.get('date_time')

    # Validate doctor_id
    session = db.session
    doctor = session.query(Doctor).filter_by(id=doctor_id).first()
    if not doctor:
        abort(400, description="Doctor ID does not exist.")

    # Validate date_time format
    try:
        date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        abort(400, description="Invalid date_time format. Please use YYYY-MM-DD HH:MM:SS.")
        
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        abort(400, description="Invalid email format.")
        
    # Validate date is not before current date
    if date_time < datetime.now():
        abort(400, description="Appointment date cannot be before the current date.")

    session = db.session

    # Check if patient exists
    patient = session.query(Patient).filter_by(email=email).first()
    if patient:
        # Check if patient has previous appointments with this doctor
        previous_appointments = session.query(Appointment).filter_by(doctor_id=doctor_id, patient_id=patient.id).count()
        if previous_appointments > 0:
            kind = 'Follow up'
        else:
            kind = 'New patient'
    else:
        patient = Patient(first_name=patient_first_name, last_name=patient_last_name, email=email)
        session.add(patient)
        session.commit()
        kind = 'New patient'
        
    existing_appointment = session.query(Appointment).filter(
        Appointment.patient_id == patient.id,
        Appointment.date_time == date_time
    ).first()
    if existing_appointment:
        abort(400, description="Patient already has an appointment at the same time.")

    # Check if start time is valid (15-minute intervals)
    if date_time.minute % 15 != 0:
        abort(400, description="Start time must be at 15-minute intervals")

    # Check if doctor has no more than 3 appointments at the same time,
    count = session.query(Appointment).filter(Appointment.doctor_id == doctor_id, Appointment.date_time == date_time).count()
    if count >= 3:
        abort(400, description="Doctor already has 3 appointments at the same time")

    new_appointment = Appointment(doctor_id=doctor_id, patient_id=patient.id, date_time=date_time, kind=kind)
    session.add(new_appointment)
    session.commit()
    return jsonify({'message': 'Appointment added successfully'})
