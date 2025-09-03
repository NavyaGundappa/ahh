from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyodbc
from datetime import datetime, timedelta, time
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import traceback

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/')
def root():
    return redirect(url_for('index'))


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/departments/')
def departments():
    return render_template('departments.html')


@app.route('/about')
def about():
    return render_template('about-us.html')


@app.route('/health-packages')
def health_packages():
    return render_template('health-packages.html')


@app.route('/sports-packages')
def sports_packages():
    return render_template('sports-packages.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/doctors')
def doctors():
    return render_template('doctors.html')


@app.route('/careers')
def careers():
    return render_template('career.html')


@app.route('/departments/general-surgery')
def general_surgery():
    return render_template('departments/general-surgery.html')


@app.route('/departments/neurosurgery')
def neurosurgery():
    return render_template('departments/neurosurgery.html')


@app.route('/departments/anaesthesia')
def anaesthesia():
    return render_template('departments/anaesthesia.html')


@app.route('/departments/pain-medicine')
def pain_medicine():
    return render_template('departments/pain-medicine.html')


@app.route('/departments/general-medicine')
def general_medicine():
    return render_template('departments/general-medicine.html')


@app.route('/departments/lab-medicine')
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


@app.route('/departments/emergency-medicine')
def emergency_medicine():
    return render_template('departments/emergency-medicine.html')


@app.route('/departments/nephrology')
def nephrology():
    return render_template('departments/nephrology.html')


@app.route('/departments/urology')
def urology():
    return render_template('departments/urology.html')


@app.route('/departments/medical-gastroenterology')
def medical_gastroenterology():
    return render_template('departments/medical-gastroenterology.html')


@app.route('/departments/minimal-access-surgery')
def minimal_access_surgery():
    return render_template('departments/minimal-access-surgery.html')


@app.route('/departments/plastic-surgery')
def plastic_surgery():
    return render_template('departments/plastic-surgery.html')


@app.route('/departments/obg')
def obg():
    return render_template('departments/obg.html')


@app.route('/departments/surgical-gastroenterology')
def surgical_gastroenterology():
    return render_template('departments/surgical-gastroenterology.html')


@app.route('/departments/radiology')
def radiology():
    return render_template('departments/radiology.html')


@app.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('terms-and-conditions.html')


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')


@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
