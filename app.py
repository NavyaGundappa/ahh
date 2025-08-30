from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyodbc
from datetime import datetime, timedelta, time
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import traceback

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/departments')
def departments():
    return render_template('departments.html')


@app.route('/about')
def about():
    return render_template('about-us.html')


@app.route('/health_packages')
def health_packages():
    return render_template('health-packages.html')


@app.route('/sports_packages')
def sports_packages():
    return render_template('sports-packages.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/doctors')
def doctors():
    return render_template('doctors.html')


@app.route('/departments/general_surgery')
def general_surgery():
    return render_template('departments/general-surgery.html')


@app.route('/departments/neurosurgery')
def neurosurgery():
    return render_template('departments/neurosurgery.html')


@app.route('/departments/anaesthesia')
def anaesthesia():
    return render_template('departments/anaesthesia.html')


@app.route('/departments/pain_medicine')
def pain_medicine():
    return render_template('departments/pain-medicine.html')


@app.route('/departments/general_medicine')
def general_medicine():
    return render_template('departments/general-medicine.html')


@app.route('/departments/lab_medicine')
def lab_medicine():
    return render_template('departments/lab-medicine.html')


@app.route('/departments/orthopaedics')
def orthopaedics():
    return render_template('departments/orthopaedics.html')


@app.route('/departments/paediatrics')
def paediatrics():
    return render_template('departments/paediatrics.html')


@app.route('/departments/physiotherapy')
def physiotherapy():
    return render_template('departments/physiotherapy.html')


@app.route('/departments/dermatology')
def dermatology():
    return render_template('departments/dermatology.html')


@app.route('/departments/ent')
def ent():
    return render_template('departments/ent.html')


@app.route('/departments/emergency_medicine')
def emergency_medicine():
    return render_template('departments/emergency-medicine.html')


@app.route('/departments/nephrology')
def nephrology():
    return render_template('departments/nephrology.html')


@app.route('/departments/urology')
def urology():
    return render_template('departments/urology.html')


@app.route('/departments/medical_gastroenterology')
def medical_gastroenterology():
    return render_template('departments/medical-gastroenterology.html')


@app.route('/departments/minimal_access_surgery')
def minimal_access_surgery():
    return render_template('departments/minimal-access-surgery.html')


@app.route('/departments/plastic_surgery')
def plastic_surgery():
    return render_template('departments/plastic-surgery.html')


@app.route('/departments/obg')
def obg():
    return render_template('departments/obg.html')


@app.route('/departments/surgical_gastroenterology')
def surgical_gastroenterology():
    return render_template('departments/surgical-gastroenterology.html')


@app.route('/departments/radiology')
def radiology():
    return render_template('departments/radiology.html')


@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('terms-and-conditions.html')


@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy-policy.html')


@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
