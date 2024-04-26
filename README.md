# Notable_doctor_schedule

## Steps to run
pip install -r requirements.txt (if this does not work, try pip3 install -r requirements.txt)

and then run:
python app.py (if this does not work, try python3 app.py)

## Design considerations:
1) Added input validations and error handling for all the edge cases like:
   - Checking for valid doctor_id in parameter/body
   - Making sure the appointment date given is > current date time
   - Checking for patient email format
   - checking for the right date_time format from param/body
2) Ensured new patient is added as 'New patient'. Patients with any prior appointments are 'Follow up'.
3) Assumed each default duration of appointment to be 15 minutes

## Recommendation:
Use Postman to check the endpoints and their responses
