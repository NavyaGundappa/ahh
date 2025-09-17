from sqlalchemy import func
import pandas as pd
from flask import request, redirect, url_for, flash, render_template
import json
from flask_migrate import Migrate
from datetime import datetime
from flask import request, send_file, render_template
from io import BytesIO
from flask import Flask, render_template, send_file
from flask import request, redirect, url_for, flash, render_template, jsonify
import tempfile
import zipfile
from flask import flash, redirect, url_for, render_template, request
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import pyodbc
from datetime import datetime, timedelta, time
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import traceback
import flash
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from models import db, Banner, Doctor, Counter, Testimonial, Speciality, Department,  HealthPackage, SportsPackage, DepartmentOverview, DepartmentService, User, UserAccess, CallbackRequest, ReviewMessage
from config import Config
import os
from functools import wraps
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config.from_object(Config)
db.init_app(app)


def create_upload_dirs():
    directories = ['banners', 'doctors', 'testimonials', 'icons']
    for directory in directories:
        path = os.path.join(app.config['UPLOAD_FOLDER'], directory)
        if not os.path.exists(path):
            os.makedirs(path)


# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    banners = Banner.query.filter_by(is_active=True).order_by(
        Banner.created_at.desc()).all()
    doctors = Doctor.query.filter_by(is_active=True).all()
    counters = Counter.query.filter_by(is_active=True).all()
    testimonials = Testimonial.query.filter_by(is_active=True).all()

    # Add this line to get specialities/departments
    specialities = Speciality.query.filter_by(
        is_active=True).order_by(Speciality.name).all()

    return render_template('index.html',
                           banners=banners,
                           doctors=doctors,
                           counters=counters,
                           testimonials=testimonials,
                           specialities=specialities)  # Add this parameter


# Departments listing page (already exists)
@app.route('/departments/')
def departments():
    departments = Department.query.filter_by(
        is_active=True).order_by(Department.name).all()
    return render_template('departments.html', departments=departments)


@app.route('/about')
def about():
    return render_template('about-us.html')


@app.route('/health-packages')
def health_packages():
    packages = HealthPackage.query.filter_by(
        is_active=True).order_by(HealthPackage.title).all()
    return render_template('health-packages.html', packages=packages)


@app.route('/sports-packages')
def sports_packages():
    packages = SportsPackage.query.filter_by(
        is_active=True).order_by(SportsPackage.title).all()
    return render_template('sports-packages.html', packages=packages)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('terms-and-conditions.html')


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')


@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

 # ADMIN Routes -----------------------------------------------------------------------------------------------------------------------------------------


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        flash("Please login first!", "warning")
        return redirect(url_for("admin_login"))

    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)

    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests']

    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    return render_template("admin/dashboard.html", access=access)


@app.route('/admin/banners', methods=['GET', 'POST'])
def admin_banners():
    if request.method == 'POST':
        title = request.form.get('title')
        alt_text = request.form.get('alt_text')

        # Ensure file is included
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['image']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Create a subfolder for banners inside UPLOAD_FOLDER
            banner_folder = os.path.join(
                app.config['UPLOAD_FOLDER'], 'banners')
            os.makedirs(banner_folder, exist_ok=True)

            # Full save path
            save_path = os.path.join(banner_folder, filename)
            file.save(save_path)

            # Path stored in DB should be relative to static/img
            # This will be "banners/filename.jpg"
            db_path = os.path.join('banners', filename).replace("\\", "/")

            # Save to DB
            banner = Banner(
                title=title,
                # This will be used in templates like <img src="{{ url_for('static', filename='img/' + banner.image_path) }}">
                image_path=db_path,
                alt_text=alt_text,

            )
            db.session.add(banner)
            db.session.commit()
            flash('Banner added successfully!')
            return redirect(url_for('admin_banners'))

    # Fetch banners for display
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('admin/banners.html', banners=banners)


@app.route('/admin/banners/delete/<int:banner_id>', methods=['POST'])
def delete_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)

    # Delete the image file from static/img/banners
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], banner.image_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete the banner from the database
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deleted successfully!')
    return redirect(url_for('admin_banners'))


@app.route('/admin/banners/edit/<int:banner_id>', methods=['GET', 'POST'])
def edit_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)

    if request.method == 'POST':
        banner.title = request.form.get('title')
        banner.alt_text = request.form.get('alt_text')

        # Check if a new file is uploaded
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                # Create banners folder if not exists
                banner_folder = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'banners')
                os.makedirs(banner_folder, exist_ok=True)

                # Delete old file if exists
                old_file_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], banner.image_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

                # Save new file
                save_path = os.path.join(banner_folder, filename)
                file.save(save_path)

                # Update DB path
                banner.image_path = os.path.join(
                    'banners', filename).replace("\\", "/")

        db.session.commit()
        flash('Banner updated successfully!')
        return redirect(url_for('admin_banners'))

    return render_template('admin/edit_banner.html', banner=banner)


# Helper function to handle file uploads

def handle_file_upload(file, folder_name):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        os.makedirs(folder_path, exist_ok=True)
        save_path = os.path.join(folder_path, filename)
        file.save(save_path)
        return f"img/{folder_name}/{filename}"
    return None


# Assuming your app, db, models, and helper functions (allowed_file, handle_file_upload, generate_department_html) are already defined


@app.route('/admin/doctors', methods=['GET', 'POST'])
def admin_doctors():
    departments = Department.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        # ----- Collect basic form data -----
        name = request.form.get('name', '').strip()
        specialization = request.form.get('specialization', '').strip()
        designation = request.form.get('designation', '').strip()
        experience = request.form.get('experience', '').strip()
        languages = request.form.get('languages', '').strip()
        bio = request.form.get('bio', '').strip()
        slug = request.form.get('slug', '').strip()
        qualification = request.form.get('qualification', '').strip()
        overview = request.form.get('overview', '').strip()
        fellowship_membership = request.form.get(
            'fellowship_membership', '').strip()
        fellowship_links = request.form.get('fellowship_links', '').strip()
        field_of_expertise = request.form.get('field_of_expertise', '').strip()
        talks_and_publications = request.form.get(
            'talks_and_publications', '').strip()
        talks_links = request.form.get('talks_links', '').strip()
        appointment_link = request.form.get('appointment_link', '').strip()
        department_slug = request.form.get('department_slug', '').strip()

        # ----- Collect timings with days -----
        time_from = request.form.getlist('time_from[]')
        time_from_period = request.form.getlist('time_from_period[]')
        time_to = request.form.getlist('time_to[]')
        time_to_period = request.form.getlist('time_to_period[]')

        timings_list = []
        for i in range(len(time_from)):
            if time_from[i] and time_to[i]:
                # Collect days for this timing row
                days = request.form.getlist(f'days[{i}][]')
                timings_list.append({
                    "from": time_from[i],
                    "from_period": time_from_period[i],
                    "to": time_to[i],
                    "to_period": time_to_period[i],
                    "days": days
                })

        timings = json.dumps(timings_list) if timings_list else None

        # ----- Validation -----
        if not name or not specialization or not department_slug:
            flash("Name, Specialization, and Department are required!", "danger")
            return redirect(url_for('admin_doctors'))

        if not slug:
            slug = name.lower().replace(' ', '-')

        # Ensure unique slug
        original_slug = slug
        counter = 1
        while Doctor.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1

        # ----- Handle image upload -----
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                doctors_folder = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'doctors')
                os.makedirs(doctors_folder, exist_ok=True)
                save_path = os.path.join(doctors_folder, filename)
                file.save(save_path)
                image_path = f"img/doctors/{filename}"

        # ----- Handle file uploads -----
        fellowship_file_path = handle_file_upload(
            request.files.get('fellowship_file'), 'fellowships')
        talks_file_path = handle_file_upload(
            request.files.get('talks_file'), 'talks')

        # ----- Save Doctor -----
        doctor = Doctor(
            name=name,
            specialization=specialization,
            designation=designation,
            experience=experience,
            qualification=qualification,
            languages=languages,
            overview=overview,
            fellowship_membership=fellowship_membership,
            fellowship_links=fellowship_links,
            fellowship_file_path=fellowship_file_path,
            field_of_expertise=field_of_expertise,
            talks_and_publications=talks_and_publications,
            talks_links=talks_links,
            talks_file_path=talks_file_path,
            bio=bio,
            slug=slug,
            image_path=image_path,
            appointment_link=appointment_link,
            department_slug=department_slug,
            timings=timings
        )
        db.session.add(doctor)
        db.session.commit()

        # ----- Regenerate department HTML -----
        department = Department.query.filter_by(slug=department_slug).first()
        if department:
            generate_department_html(department)

        flash('Doctor added successfully!', 'success')
        return redirect(url_for('admin_doctors'))

    # ----- Fetch doctors for display -----
    doctors = Doctor.query.order_by(Doctor.name).all()

    # ----- Parse timings and aggregate days for template -----
    for d in doctors:
        try:
            d.timings_parsed = json.loads(d.timings) if d.timings else []

            # Collect all unique days across all timings
            all_days = []
            for t in d.timings_parsed:
                if t.get("days"):
                    all_days.extend(t["days"])
            # Remove duplicates while preserving order
            d.days_parsed = list(dict.fromkeys(all_days))
        except Exception:
            d.timings_parsed = []
            d.days_parsed = []

    return render_template('admin/doctors.html', doctors=doctors, departments=departments)


@app.route('/admin/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    departments = Department.query.filter_by(is_active=True).all()
    old_department_slug = doctor.department_slug

    if request.method == 'POST':
        # ----- Collect form data -----
        name = request.form.get('name', '').strip()
        specialization = request.form.get('specialization', '').strip()
        designation = request.form.get('designation', '').strip()
        experience = request.form.get('experience', '').strip()
        languages = request.form.get('languages', '').strip()
        bio = request.form.get('bio', '').strip()
        slug = request.form.get('slug', '').strip()
        qualification = request.form.get('qualification', '').strip()
        overview = request.form.get('overview', '').strip()
        fellowship_membership = request.form.get(
            'fellowship_membership', '').strip()
        fellowship_links = request.form.get('fellowship_links', '').strip()
        field_of_expertise = request.form.get('field_of_expertise', '').strip()
        talks_and_publications = request.form.get(
            'talks_and_publications', '').strip()
        talks_links = request.form.get('talks_links', '').strip()
        appointment_link = request.form.get('appointment_link', '').strip()
        department_slug = request.form.get('department_slug', '').strip()

        # ----- Collect timings -----
        time_from = request.form.getlist('time_from[]')
        time_from_period = request.form.getlist('time_from_period[]')
        time_to = request.form.getlist('time_to[]')
        time_to_period = request.form.getlist('time_to_period[]')

        timings_list = []
        for i in range(len(time_from)):
            if time_from[i] and time_to[i]:
                days = request.form.getlist(f'days[{i}][]')
                timings_list.append({
                    "days": days,
                    "from": time_from[i],
                    "from_period": time_from_period[i],
                    "to": time_to[i],
                    "to_period": time_to_period[i]
                })
        doctor.timings = json.dumps(timings_list) if timings_list else None

        # ----- Validation -----
        if not name or not specialization or not department_slug:
            flash("Name, Specialization, and Department are required!", "danger")
            return redirect(url_for('edit_doctor', doctor_id=doctor_id))

        if not slug:
            slug = name.lower().replace(' ', '-')

        # Ensure unique slug
        original_slug = slug
        counter = 1
        while Doctor.query.filter(Doctor.slug == slug, Doctor.id != doctor.id).first():
            slug = f"{original_slug}-{counter}"
            counter += 1

        # ----- Handle image upload -----
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                doctors_folder = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'doctors')
                os.makedirs(doctors_folder, exist_ok=True)
                save_path = os.path.join(doctors_folder, filename)
                file.save(save_path)
                doctor.image_path = f"img/doctors/{filename}"

        # ----- Handle fellowship/talks uploads -----
        if 'fellowship_file' in request.files:
            fellowship_file = request.files['fellowship_file']
            if fellowship_file and fellowship_file.filename != '' and allowed_file(fellowship_file.filename):
                if doctor.fellowship_file_path:
                    old_file_path = os.path.join(
                        app.static_folder, doctor.fellowship_file_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                doctor.fellowship_file_path = handle_file_upload(
                    fellowship_file, 'fellowships')

        if 'talks_file' in request.files:
            talks_file = request.files['talks_file']
            if talks_file and talks_file.filename != '' and allowed_file(talks_file.filename):
                if doctor.talks_file_path:
                    old_file_path = os.path.join(
                        app.static_folder, doctor.talks_file_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                doctor.talks_file_path = handle_file_upload(
                    talks_file, 'talks')

        # ----- Update fields -----
        doctor.name = name
        doctor.specialization = specialization
        doctor.designation = designation
        doctor.experience = experience
        doctor.languages = languages
        doctor.bio = bio
        doctor.slug = slug
        doctor.qualification = qualification
        doctor.overview = overview
        doctor.fellowship_membership = fellowship_membership
        doctor.fellowship_links = fellowship_links
        doctor.field_of_expertise = field_of_expertise
        doctor.talks_and_publications = talks_and_publications
        doctor.talks_links = talks_links
        doctor.appointment_link = appointment_link
        doctor.department_slug = department_slug

        db.session.commit()

        # ----- Regenerate department HTMLs -----
        if old_department_slug != department_slug:
            old_department = Department.query.filter_by(
                slug=old_department_slug).first()
            if old_department:
                generate_department_html(old_department)

        new_department = Department.query.filter_by(
            slug=department_slug).first()
        if new_department:
            generate_department_html(new_department)

        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('admin_doctors'))

    # ----- Parse timings for edit form -----
    try:
        doctor.timings_parsed = json.loads(
            doctor.timings) if doctor.timings else []
        all_days = []
        for t in doctor.timings_parsed:
            if t.get("days"):
                all_days.extend(t["days"])
        doctor.days_parsed = list(dict.fromkeys(all_days))
    except Exception:
        doctor.timings_parsed = []
        doctor.days_parsed = []

    return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)


@app.route('/admin/doctors/delete/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    # Store department slug for regeneration
    department_slug = doctor.department_slug

    # Optionally, delete the uploaded image file from static folder
    if doctor.image_path:
        image_full_path = os.path.join(
            app.config['UPLOAD_FOLDER'], doctor.image_path)
        if os.path.exists(image_full_path):
            os.remove(image_full_path)

    # Delete doctor from DB
    db.session.delete(doctor)
    db.session.commit()

    # Regenerate the department HTML after deleting doctor
    department = Department.query.filter_by(slug=department_slug).first()
    if department:
        generate_department_html(department)

    flash(f'Doctor "{doctor.name}" has been deleted!', 'success')
    return redirect(url_for('admin_doctors'))


# --- Utility function to generate HTML ---


def generate_department_html(department):
    """Generates a department Jinja template file (keeps base.html inheritance)."""

    # Existing code for file_content
    file_content = """
{% extends "base.html" %}

{% block title %}{{ department.name }} - Aarogya Hastha{% endblock %}

{% block content %}
<section class="department-banner" data-aos="fade-up" data-aos-offset="300" data-aos-easing="ease-in-sine">
    <div class="container">
        <div class="banner">
            {% if department.banner_path %}
                <img loading="lazy" src="{{ url_for('static', filename=department.banner_path) }}" alt="{{ department.name }}">
            {% else %}
                <img loading="lazy" src="/static/img/banners/default.jpg" alt="{{ department.name }}">
            {% endif %}
            <div class="text-box-1">
                <h1>{{ department.name }}</h1>
                <p>{{ department.description }}</p>
            </div>
        </div>
    </div>
</section>

<div class="container my-5">
 <ul class="nav nav-tabs" id="departmentTabs" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active fw-bold text-dark" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview-tab-pane" type="button" role="tab" aria-controls="overview-tab-pane" aria-selected="true">Overview</button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link fw-bold text-dark" id="services-tab" data-bs-toggle="tab" data-bs-target="#services-tab-pane" type="button" role="tab" aria-controls="services-tab-pane" aria-selected="false">Our Services</button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link fw-bold text-dark" id="specialists-tab" data-bs-toggle="tab" data-bs-target="#specialists-tab-pane" type="button" role="tab" aria-controls="specialists-tab-pane" aria-selected="false">Our Specialists</button>
    </li>
</ul>

    <div class="tab-content" id="departmentTabsContent">

        <div class="tab-pane fade show active" id="overview-tab-pane" role="tabpanel" aria-labelledby="overview-tab">
            <section data-aos="fade-up" class="py-4">
                {% if overview %}
                <blockquote class="blockquote blockquote-custom">
                    <p class="mb-0 mt-2">{{ overview.quote }}</p>
                    <div class="blockquote-footer mt-4 text-end">{{ overview.quote_author }}</div>
                </blockquote>
                <p>{{ overview.content }}</p>
                {% endif %}
            </section>
        </div>
        

<div class="tab-pane fade" id="services-tab-pane" role="tabpanel" aria-labelledby="services-tab">
    <section class="department-section py-4">
        <h2>Types of {{ department.name }} Care</h2>
        <div class="row g-4">
            {% for service in services %}
            <div class="col-md-6">
                <div class="card h-100 p-3">
                    {% if service.icon_path %}
                    <img src="{{ url_for('static', filename=service.icon_path) }}" alt="{{ service.title }}" class="card-img-top" style="max-width: 60px;">
                    {% endif %}
                    <div class="card-body">
                        <h4 class="card-title text-dark-blue">{{ service.title }}</h4>
                        {% if service.list_items %}
                        <ul class="card-text list-unstyled">
                            {% for item in service.get_list_items() %}
                            <li><i class="fas fa-check-circle text-success me-2"></i>{{ item }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                        <p class="card-text">{{ service.description }}</p>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </section>
</div>

<div class="tab-pane fade" id="specialists-tab-pane" role="tabpanel" aria-labelledby="specialists-tab">
    <section class="py-4">
        <h2>Our Specialists</h2>
        <div id="specialists-list" class="appointment-section">
            <div class="row g-3">
                {% set ns = namespace(has_doctors=False) %}
                
                {% for doctor in doctors %}
                    {% if doctor.is_active %}
                        {% set ns.has_doctors = True %}
                        <div class="col-lg-6 specialist-item" data-specialist="{{ doctor.slug }}">
                            <div class="specialist-card">
                                <div class="img-box">
                                    {% if doctor.image_path %}
                                        <img class="img-fluid" src="{{ url_for('static', filename=doctor.image_path) }}" alt="{{ doctor.name }}">
                                    {% else %}
                                        <img class="img-fluid" src="{{ url_for('static', filename='img/default-doctor.jpg') }}" alt="No Image">
                                    {% endif %}
                                </div>
                                <div class="content">
                                    <h3>{{ doctor.name }}</h3>
                                    <h4>{{ doctor.specialization }}</h4>
                                    {% if doctor.day_from and doctor.day_to and doctor.time_from_hour %}
                                        <p class="details">
                                            <b>Timings:</b>
                                            {{ doctor.day_from }} - {{ doctor.day_to }},
                                            {{ doctor.time_from_hour }}:{{ doctor.time_from_min }} {{ doctor.time_from_ampm }} -
                                            {{ doctor.time_to_hour }}:{{ doctor.time_to_min }} {{ doctor.time_to_ampm }}
                                        </p>
                                    {% endif %}
                                    <a class="book-btn" target="_blank" href="{{ doctor.appointment_link or 'https://app.fyndbetter.com/ahh_apt' }}">
                                        BOOK APPOINTMENT
                                    </a>
                                </div>
                            </div>
                        </div>
                    {% endif %}
                {% endfor %}

                {% if not ns.has_doctors %}
                <div class="col-12">
                    <div class="alert alert-warning">
                        No specialists found for this department.
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </section>
</div>


<script>
    function showDescription(index) {
        let desc = document.getElementById("desc-" + index).innerHTML;
        document.getElementById("description-container").innerHTML = desc;
    }
</script>

<section data-aos-easing="ease-in-sine" class="service-carousel-section py-5">
    <div class="container d-flex justify-content-center">
        <div class="owl-carousel service-carousel">
            </div>
    </div>
</section>

<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="/static/js/bootstrap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js"></script>
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script src="/static/js/script.js"></script>
<script src="https://fyndbetter.com/chatbot/aarogya_chatbot"></script>
<script>
    $(".book-apt").on('click', function () {
        var url = $(this).data("url");
        window.open(url, '_blank');
    });
</script>
<a href="#" id="scrollToTopBtn" class="scroll-to-top-btn" title="Scroll to top" aria-label="Scroll to top">
    <i class="fa fa-arrow-up"></i>
</a>
<script> $(document).ready(function () { initDepartmentPageActions(); }) </script>
{% endblock %}
    """

    # Wrap the file creation logic in an application context
    with app.app_context():
        # Save into templates/departments/<slug>.html
        output_folder = os.path.join(app.template_folder, "departments")
        os.makedirs(output_folder, exist_ok=True)
        file_path = os.path.join(output_folder, f"{department.slug}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content.strip())


@app.route('/admin/counters', methods=['GET', 'POST'])
def admin_counters():
    if request.method == 'POST':
        label = request.form.get('label')
        count = request.form.get('count')
        suffix = request.form.get('suffix', '+')

        # Handle icon upload
        icon_file = request.files.get('icon_file')
        icon_path = None
        if icon_file and icon_file.filename != '':
            filename = secure_filename(icon_file.filename)
            icons_folder = os.path.join(app.static_folder, 'icons')
            os.makedirs(icons_folder, exist_ok=True)
            full_path = os.path.join(icons_folder, filename)
            icon_file.save(full_path)
            icon_path = f'icons/{filename}'  # relative path for frontend

        counter = Counter(
            label=label,
            count=int(count),
            suffix=suffix,
            icon_path=icon_path
        )
        db.session.add(counter)
        db.session.commit()
        flash('Counter added successfully!')
        return redirect(url_for('admin_counters'))

    counters = Counter.query.all()
    return render_template('admin/counters.html', counters=counters)


@app.route('/admin/counters/edit/<int:counter_id>', methods=['GET', 'POST'])
def edit_counter(counter_id):
    counter = Counter.query.get_or_404(counter_id)

    if request.method == 'POST':
        counter.label = request.form.get('label')
        counter.count = int(request.form.get('count'))
        counter.suffix = request.form.get('suffix', '+')

        # Handle icon upload (optional)
        icon_file = request.files.get('icon_file')
        if icon_file and icon_file.filename != '':
            filename = secure_filename(icon_file.filename)
            icons_folder = os.path.join(app.static_folder, 'icons')
            os.makedirs(icons_folder, exist_ok=True)
            full_path = os.path.join(icons_folder, filename)
            icon_file.save(full_path)
            counter.icon_path = f'icons/{filename}'  # update path

        db.session.commit()
        flash('Counter updated successfully!', 'success')
        return redirect(url_for('admin_counters'))

    return render_template('admin/edit_counter.html', counter=counter)


@app.route('/admin/counters/delete/<int:counter_id>', methods=['POST'])
def delete_counter(counter_id):
    counter = Counter.query.get_or_404(counter_id)

    # Delete the associated icon file if it exists
    if counter.icon_path:
        icon_full_path = os.path.join(app.static_folder, counter.icon_path)
        if os.path.exists(icon_full_path):
            os.remove(icon_full_path)

    db.session.delete(counter)
    db.session.commit()
    flash('Counter deleted successfully!', 'success')
    return redirect(url_for('admin_counters'))


@app.route('/admin/testimonials', methods=['GET', 'POST'])
def admin_testimonials():
    if request.method == 'POST':
        alt_text = request.form.get('alt_text', '')

        if 'image' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join('testimonials', filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filepath)

            # Ensure folder exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            file.save(save_path)

            testimonial = Testimonial(image_path=filepath, alt_text=alt_text)
            db.session.add(testimonial)
            db.session.commit()
            flash('Testimonial added successfully!', 'success')
            return redirect(url_for('admin_testimonials'))

    testimonials = Testimonial.query.order_by(
        Testimonial.created_at.desc()).all()
    return render_template('admin/testimonials.html', testimonials=testimonials)

# Route to delete testimonial


@app.route('/admin/testimonials/delete/<int:testimonial_id>', methods=['POST'])
def delete_testimonial(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)

    # Delete image file from static folder if exists
    if testimonial.image_path:
        image_path = os.path.join(
            app.config['UPLOAD_FOLDER'], testimonial.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(testimonial)
    db.session.commit()
    flash('Testimonial deleted successfully!', 'success')
    return redirect(url_for('admin_testimonials'))


# API endpoints for toggling active status
@app.route('/api/toggle_banner/<int:id>', methods=['POST'])
def toggle_banner(id):
    banner = Banner.query.get_or_404(id)
    banner.is_active = not banner.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': banner.is_active})


@app.route('/api/toggle_doctor/<int:id>', methods=['POST'])
def toggle_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    doctor.is_active = not doctor.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': doctor.is_active})


@app.route('/api/toggle_counter/<int:id>', methods=['POST'])
def toggle_counter(id):
    counter = Counter.query.get_or_404(id)
    counter.is_active = not counter.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': counter.is_active})


@app.route('/api/toggle_testimonial/<int:id>', methods=['POST'])
def toggle_testimonial(id):
    testimonial = Testimonial.query.get_or_404(id)
    testimonial.is_active = not testimonial.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': testimonial.is_active})


@app.route('/admin/doctors/bulk-upload', methods=['POST'])
def bulk_upload_doctors():
    excel_file = request.files.get('excel_file')
    images_zip = request.files.get('images_zip')

    if not excel_file:
        flash("Please upload an Excel file.", "danger")
        return redirect(url_for('admin_doctors'))

    # Extract images zip if provided
    images_folder = None
    images_map = {}
    if images_zip and images_zip.filename.endswith('.zip'):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(images_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        images_folder = temp_dir

        # Map filenames (case-insensitive)
        for root, _, files in os.walk(images_folder):
            for file in files:
                images_map[file.lower().strip()] = os.path.join(root, file)

    # Read Excel
    df = pd.read_excel(excel_file)
    added_count = 0

    for _, row in df.iterrows():
        name = str(row.get('name', '')).strip()
        specialization = str(row.get('specialization', '')).strip()
        bio = str(row.get('bio', '')).strip()
        slug = str(row.get('slug', '')).strip()
        image_filename = str(row.get('image_filename', '')).strip()

        if not name or not specialization:
            continue

        # Generate slug if empty
        if not slug:
            slug = name.lower().replace(' ', '-')

        # Ensure slug uniqueness
        original_slug = slug
        counter = 1
        while Doctor.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Handle image file
        image_path = None
        if images_folder and image_filename:
            key = image_filename.lower().strip()
            if key in images_map:
                src_path = images_map[key]
                doctors_folder = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'doctors')
                os.makedirs(doctors_folder, exist_ok=True)
                dest_path = os.path.join(
                    doctors_folder, secure_filename(os.path.basename(src_path)))
                os.replace(src_path, dest_path)
                image_path = os.path.join('doctors', secure_filename(
                    os.path.basename(src_path))).replace("\\", "/")

        # Add doctor to DB
        doctor = Doctor(
            name=name,
            specialization=specialization,
            bio=bio,
            slug=slug,
            image_path=image_path
        )
        db.session.add(doctor)
        added_count += 1

    db.session.commit()
    flash(f"{added_count} doctors added successfully!", "success")
    return redirect(url_for('admin_doctors'))

# our speciaties start-------------------------

# Allowed file extensions for speciality thumbnails


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin/specialities', methods=['GET', 'POST'])
def admin_specialities():
    if request.method == 'POST':
        # Check if it's a delete request
        if 'delete_id' in request.form:
            speciality_id = request.form.get('delete_id')
            speciality = Speciality.query.get_or_404(speciality_id)

            # Delete the associated thumbnail file if it exists
            if speciality.thumbnail_path:
                thumbnail_full_path = os.path.join(
                    app.static_folder, speciality.thumbnail_path)
                if os.path.exists(thumbnail_full_path):
                    os.remove(thumbnail_full_path)

            db.session.delete(speciality)
            db.session.commit()
            flash('Speciality deleted successfully!', 'success')
            return redirect(url_for('admin_specialities'))

        # Check if it's an edit request
        speciality_id = request.form.get('speciality_id')
        if speciality_id:
            # Update existing speciality
            speciality = Speciality.query.get_or_404(speciality_id)
            speciality.name = request.form.get('name')
            speciality.slug = request.form.get('slug')
            speciality.description = request.form.get('description')

            # Handle thumbnail update
            thumbnail_file = request.files.get('thumbnail')
            if thumbnail_file and thumbnail_file.filename != '':
                if allowed_file(thumbnail_file.filename):
                    # Delete old thumbnail if exists
                    if speciality.thumbnail_path:
                        old_thumbnail_path = os.path.join(
                            app.static_folder, speciality.thumbnail_path)
                        if os.path.exists(old_thumbnail_path):
                            os.remove(old_thumbnail_path)

                    # Save new thumbnail
                    filename = secure_filename(thumbnail_file.filename)
                    thumbs_folder = os.path.join(
                        app.static_folder, 'img', 'department', 'thumbs')
                    os.makedirs(thumbs_folder, exist_ok=True)
                    full_path = os.path.join(thumbs_folder, filename)
                    thumbnail_file.save(full_path)
                    speciality.thumbnail_path = f'img/department/thumbs/{filename}'
                else:
                    flash(
                        'Invalid file type for thumbnail. Allowed: png, jpg, jpeg, gif, svg', 'error')
                    return redirect(url_for('admin_specialities'))

            db.session.commit()
            flash('Speciality updated successfully!', 'success')
            return redirect(url_for('admin_specialities'))
        else:
            # Add new speciality
            name = request.form.get('name')
            slug = request.form.get('slug')
            description = request.form.get('description')

            # Check if speciality with same slug already exists
            existing = Speciality.query.filter_by(slug=slug).first()
            if existing:
                flash('A speciality with this slug already exists.', 'error')
                return redirect(url_for('admin_specialities'))

            # Handle thumbnail upload
            thumbnail_path = None
            thumbnail_file = request.files.get('thumbnail')
            if thumbnail_file and thumbnail_file.filename != '':
                if allowed_file(thumbnail_file.filename):
                    filename = secure_filename(thumbnail_file.filename)
                    # Create directory if it doesn't exist
                    thumbs_folder = os.path.join(
                        app.static_folder, 'img', 'department', 'thumbs')
                    os.makedirs(thumbs_folder, exist_ok=True)
                    full_path = os.path.join(thumbs_folder, filename)
                    thumbnail_file.save(full_path)
                    # relative path for frontend
                    thumbnail_path = f'img/department/thumbs/{filename}'
                else:
                    flash(
                        'Invalid file type for thumbnail. Allowed: png, jpg, jpeg, gif, svg', 'error')
                    return redirect(url_for('admin_specialities'))

            speciality = Speciality(
                name=name,
                slug=slug,
                description=description,
                thumbnail_path=thumbnail_path
            )

            db.session.add(speciality)
            db.session.commit()
            flash('Speciality added successfully!', 'success')
            return redirect(url_for('admin_specialities'))

    specialities = Speciality.query.order_by(Speciality.name).all()
    return render_template('admin/specialities.html', specialities=specialities)


@app.route('/admin/specialities/toggle/<int:speciality_id>', methods=['POST'])
def toggle_speciality(speciality_id):
    speciality = Speciality.query.get_or_404(speciality_id)
    speciality.is_active = not speciality.is_active
    db.session.commit()

    status = "activated" if speciality.is_active else "deactivated"
    flash(f'Speciality {status} successfully!', 'success')
    return redirect(url_for('admin_specialities'))
# our speciaties end


# departments-----------------
@app.route('/admin/departments', methods=['GET', 'POST'])
def admin_departments():
    if request.method == 'POST':
        # ------------------ DELETE DEPARTMENT ------------------
        if 'delete_id' in request.form:
            dept_id = request.form.get('delete_id')
            department = Department.query.get_or_404(dept_id)

            # Delete associated icon file if exists
            if department.icon_path:
                icon_full_path = os.path.join(
                    app.static_folder, department.icon_path)
                if os.path.exists(icon_full_path):
                    os.remove(icon_full_path)

            # Delete associated banner file if exists
            if department.banner_path:
                banner_full_path = os.path.join(
                    app.static_folder, department.banner_path)
                if os.path.exists(banner_full_path):
                    os.remove(banner_full_path)

            db.session.delete(department)
            db.session.commit()
            flash("Department deleted successfully!", "success")
            return redirect(url_for('admin_departments'))

        # ------------------ UPDATE DEPARTMENT ------------------
        dept_id = request.form.get('department_id')
        if dept_id:
            department = Department.query.get_or_404(dept_id)
            department.name = request.form.get('name')
            department.slug = request.form.get('slug')
            department.description = request.form.get('description')

            # ---- Handle Icon Update ----
            icon_file = request.files.get('icon')
            if icon_file and icon_file.filename != '':
                if allowed_file(icon_file.filename):
                    if department.icon_path:
                        old_icon_path = os.path.join(
                            app.static_folder, department.icon_path)
                        if os.path.exists(old_icon_path):
                            os.remove(old_icon_path)

                    filename = secure_filename(icon_file.filename)
                    icons_folder = os.path.join(
                        app.static_folder, 'img', 'department', 'icons')
                    os.makedirs(icons_folder, exist_ok=True)
                    full_path = os.path.join(icons_folder, filename)
                    icon_file.save(full_path)
                    department.icon_path = f'img/department/icons/{filename}'
                else:
                    flash(
                        'Invalid file type for icon. Allowed: png, jpg, jpeg, gif, svg', 'error')
                    return redirect(url_for('admin_departments'))

            # ---- Handle Banner Update ----
            banner_file = request.files.get('banner')
            if banner_file and banner_file.filename != '':
                if allowed_file(banner_file.filename):
                    if department.banner_path:
                        old_banner_path = os.path.join(
                            app.static_folder, department.banner_path)
                        if os.path.exists(old_banner_path):
                            os.remove(old_banner_path)

                    filename = secure_filename(banner_file.filename)
                    banners_folder = os.path.join(
                        app.static_folder, 'img', 'department', 'banners')
                    os.makedirs(banners_folder, exist_ok=True)
                    full_path = os.path.join(banners_folder, filename)
                    banner_file.save(full_path)
                    department.banner_path = f'img/department/banners/{filename}'
                else:
                    flash(
                        'Invalid file type for banner. Allowed: png, jpg, jpeg, gif, svg', 'error')
                    return redirect(url_for('admin_departments'))

            db.session.commit()
            flash("Department updated successfully!", "success")
            return redirect(url_for('admin_departments'))

        # ------------------ ADD NEW DEPARTMENT ------------------
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description')

        existing = Department.query.filter_by(slug=slug).first()
        if existing:
            flash("A department with this slug already exists.", "error")
            return redirect(url_for('admin_departments'))

        # ---- Save Icon ----
        icon_path = None
        icon_file = request.files.get('icon')
        if icon_file and icon_file.filename != '':
            if allowed_file(icon_file.filename):
                filename = secure_filename(icon_file.filename)
                icons_folder = os.path.join(
                    app.static_folder, 'img', 'department', 'icons')
                os.makedirs(icons_folder, exist_ok=True)
                full_path = os.path.join(icons_folder, filename)
                icon_file.save(full_path)
                icon_path = f'img/department/icons/{filename}'
            else:
                flash(
                    'Invalid file type for icon. Allowed: png, jpg, jpeg, gif, svg', 'error')
                return redirect(url_for('admin_departments'))

        # ---- Save Banner ----
        banner_path = None
        banner_file = request.files.get('banner')
        if banner_file and banner_file.filename != '':
            if allowed_file(banner_file.filename):
                filename = secure_filename(banner_file.filename)
                banners_folder = os.path.join(
                    app.static_folder, 'img', 'department', 'banners')
                os.makedirs(banners_folder, exist_ok=True)
                full_path = os.path.join(banners_folder, filename)
                banner_file.save(full_path)
                banner_path = f'img/department/banners/{filename}'
            else:
                flash(
                    'Invalid file type for banner. Allowed: png, jpg, jpeg, gif, svg', 'error')
                return redirect(url_for('admin_departments'))

        department = Department(
            name=name,
            slug=slug,
            description=description,
            icon_path=icon_path,
            banner_path=banner_path
        )
        db.session.add(department)
        db.session.commit()
        flash("Department added successfully!", "success")
        return redirect(url_for('admin_departments'))

    # ------------------ GET DEPARTMENTS ------------------
    departments = Department.query.order_by(Department.name).all()
    return render_template('admin/departments.html', departments=departments)

# departments -------end

# healht package start


@app.route('/admin/health-packages', methods=['GET', 'POST'])
def admin_health_packages():
    if request.method == 'POST':
        # Delete Package
        if 'delete_id' in request.form:
            package_id = request.form.get('delete_id')
            package = HealthPackage.query.get_or_404(package_id)

            db.session.delete(package)
            db.session.commit()
            flash("Health package deleted successfully!", "success")
            return redirect(url_for('admin_health_packages'))

        # Update Package
        package_id = request.form.get('package_id')
        if package_id:
            package = HealthPackage.query.get_or_404(package_id)
            package.title = request.form.get('title')
            package.slug = request.form.get('slug')
            package.gender = request.form.get('gender')
            package.original_price = float(request.form.get('original_price'))
            package.offer_price = float(request.form.get('offer_price'))
            package.is_best_value = 'is_best_value' in request.form
            package.description = request.form.get('description')

            # Process tests (convert from textarea to list then to string)
            tests_text = request.form.get('tests', '')
            tests_list = [test.strip()
                          for test in tests_text.split('\n') if test.strip()]
            package.tests = ','.join(tests_list)

            package.important_info = request.form.get('important_info')

            db.session.commit()
            flash("Health package updated successfully!", "success")
            return redirect(url_for('admin_health_packages'))

        # Add New Package
        title = request.form.get('title')
        slug = request.form.get('slug')
        gender = request.form.get('gender')
        original_price = float(request.form.get('original_price'))
        offer_price = float(request.form.get('offer_price'))
        is_best_value = 'is_best_value' in request.form
        description = request.form.get('description')

        # Process tests
        tests_text = request.form.get('tests', '')
        tests_list = [test.strip()
                      for test in tests_text.split('\n') if test.strip()]
        tests = ','.join(tests_list)

        important_info = request.form.get('important_info')

        # Calculate discount percentage
        discount_percentage = ((original_price - offer_price) /
                               original_price) * 100 if original_price > 0 else 0

        # Check if package with same slug already exists
        existing = HealthPackage.query.filter_by(slug=slug).first()
        if existing:
            flash("A health package with this slug already exists.", "error")
            return redirect(url_for('admin_health_packages'))

        package = HealthPackage(
            title=title,
            slug=slug,
            gender=gender,
            original_price=original_price,
            offer_price=offer_price,
            discount_percentage=discount_percentage,
            is_best_value=is_best_value,
            description=description,
            tests=tests,
            important_info=important_info
        )

        db.session.add(package)
        db.session.commit()
        flash("Health package added successfully!", "success")
        return redirect(url_for('admin_health_packages'))

    packages = HealthPackage.query.order_by(HealthPackage.title).all()
    return render_template('admin/health-packages.html', packages=packages)


@app.route('/api/toggle_package/<int:package_id>', methods=['POST'])
def toggle_package(package_id):
    package = HealthPackage.query.get_or_404(package_id)
    package.is_active = not package.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': package.is_active})

# healthpackage end

# sportspackage start


@app.route('/admin/sports-packages', methods=['GET', 'POST'])
def admin_sports_packages():
    if request.method == 'POST':
        # Delete Package
        if 'delete_id' in request.form:
            package_id = request.form.get('delete_id')
            package = SportsPackage.query.get_or_404(package_id)

            db.session.delete(package)
            db.session.commit()
            flash("Sports package deleted successfully!", "success")
            return redirect(url_for('admin_sports_packages'))

        # Update Package
        package_id = request.form.get('package_id')
        if package_id:
            package = SportsPackage.query.get_or_404(package_id)
            package.title = request.form.get('title')
            package.slug = request.form.get('slug')
            package.sport_type = request.form.get('sport_type')
            package.original_price = float(request.form.get('original_price'))
            package.offer_price = float(request.form.get('offer_price'))
            package.is_best_value = 'is_best_value' in request.form
            package.description = request.form.get('description')

            # Process tests (convert from textarea to list then to string)
            tests_text = request.form.get('tests', '')
            tests_list = [test.strip()
                          for test in tests_text.split('\n') if test.strip()]
            package.tests = ','.join(tests_list)

            package.important_info = request.form.get('important_info')

            # Calculate discount percentage
            if package.original_price > 0:
                package.discount_percentage = (
                    (package.original_price - package.offer_price) / package.original_price) * 100

            db.session.commit()
            flash("Sports package updated successfully!", "success")
            return redirect(url_for('admin_sports_packages'))

        # Add New Package
        title = request.form.get('title')
        slug = request.form.get('slug')
        sport_type = request.form.get('sport_type')
        original_price = float(request.form.get('original_price'))
        offer_price = float(request.form.get('offer_price'))
        is_best_value = 'is_best_value' in request.form
        description = request.form.get('description')

        # Process tests
        tests_text = request.form.get('tests', '')
        tests_list = [test.strip()
                      for test in tests_text.split('\n') if test.strip()]
        tests = ','.join(tests_list)

        important_info = request.form.get('important_info')

        # Calculate discount percentage
        discount_percentage = ((original_price - offer_price) /
                               original_price) * 100 if original_price > 0 else 0

        # Check if package with same slug already exists
        existing = SportsPackage.query.filter_by(slug=slug).first()
        if existing:
            flash("A sports package with this slug already exists.", "error")
            return redirect(url_for('admin_sports_packages'))

        package = SportsPackage(
            title=title,
            slug=slug,
            sport_type=sport_type,
            original_price=original_price,
            offer_price=offer_price,
            discount_percentage=discount_percentage,
            is_best_value=is_best_value,
            description=description,
            tests=tests,
            important_info=important_info
        )

        db.session.add(package)
        db.session.commit()
        flash("Sports package added successfully!", "success")
        return redirect(url_for('admin_sports_packages'))

    packages = SportsPackage.query.order_by(SportsPackage.title).all()
    return render_template('admin/sports_package.html', packages=packages)


@app.route('/api/toggle_sports_package/<int:package_id>', methods=['POST'])
def toggle_sports_package(package_id):
    package = SportsPackage.query.get_or_404(package_id)
    package.is_active = not package.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': package.is_active})
# sportspackage end


@app.route('/departments/<slug>')
def department_page(slug):
    department = Department.query.filter_by(
        slug=slug, is_active=True).first_or_404()

    overview = DepartmentOverview.query.filter_by(
        department_id=department.id).first()
    services = DepartmentService.query.filter_by(
        department_id=department.id, is_active=True).all()

    # Fetch doctors for this department
    doctors = Doctor.query.filter_by(
        department_slug=slug, is_active=True).all()

    template_path = f"departments/{slug}.html"
    if os.path.exists(os.path.join(app.template_folder, template_path)):
        return render_template(template_path, department=department, overview=overview, services=services, doctors=doctors)

    return render_template("department.html", department=department, overview=overview, services=services, doctors=doctors)


# ------------------ ADMIN: Department Overview ------------------
@app.route('/admin/department_overview', methods=['GET', 'POST'])
def admin_department_overview():
    if request.method == 'POST':
        overview_id = request.form.get('overview_id')
        department_id = request.form.get('department_id')

        if overview_id:  # UPDATE
            overview = DepartmentOverview.query.get_or_404(overview_id)
            overview.content = request.form.get('content')
            overview.quote = request.form.get('quote')
            overview.quote_author = request.form.get('quote_author')
            overview.department_id = department_id
            db.session.commit()
            flash("Overview updated successfully!", "success")
        else:  # ADD
            overview = DepartmentOverview(
                content=request.form.get('content'),
                quote=request.form.get('quote'),
                quote_author=request.form.get('quote_author'),
                department_id=department_id
            )
            db.session.add(overview)
            db.session.commit()
            flash("Overview added successfully!", "success")

        # Regenerate the department HTML after changes
        department = Department.query.get(department_id)
        if department:
            generate_department_html(department)

        return redirect(url_for('admin_department_overview'))

    overviews = DepartmentOverview.query.all()
    departments = Department.query.all()
    return render_template("admin/department_overview.html", overviews=overviews, departments=departments)


# ------------------ ADMIN: Department Services ------------------
@app.route('/admin/department_services', methods=['GET', 'POST'])
def admin_department_services():
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        department_id = request.form.get('department_id')

        if service_id:  # UPDATE
            service = DepartmentService.query.get_or_404(service_id)
            service.title = request.form.get('title')
            service.description = request.form.get('description')
            service.list_items = request.form.get(
                'list_items')  # comma separated
            service.department_id = department_id

            # Handle icon upload
            if 'icon' in request.files:
                icon = request.files['icon']
                if icon and icon.filename != '':
                    filename = secure_filename(icon.filename)
                    filepath = os.path.join(
                        app.config['UPLOAD_FOLDER'], filename)
                    icon.save(filepath)
                    service.icon_path = f'img/department/icons/{filename}'

            db.session.commit()
            flash("Service updated successfully!", "success")

        else:  # ADD NEW
            icon_path = None
            if 'icon' in request.files:
                icon = request.files['icon']
                if icon and icon.filename != '':
                    filename = secure_filename(icon.filename)
                    filepath = os.path.join(
                        app.config['UPLOAD_FOLDER'], filename)
                    icon.save(filepath)
                    icon_path = f'img/department/icons/{filename}'

            service = DepartmentService(
                title=request.form.get('title'),
                description=request.form.get('description'),
                list_items=request.form.get('list_items'),
                department_id=department_id,
                icon_path=icon_path
            )
            db.session.add(service)
            db.session.commit()
            flash("Service added successfully!", "success")

        # Regenerate the department HTML after changes
        department = Department.query.get(department_id)
        if department:
            generate_department_html(department)

        return redirect(url_for('admin_department_services'))

    services = DepartmentService.query.all()
    departments = Department.query.all()
    return render_template("admin/department_services.html", services=services, departments=departments)


@app.route('/admin/delete_overview/<int:id>', methods=['POST'])
def delete_overview(id):
    overview = DepartmentOverview.query.get_or_404(id)
    department_id = overview.department_id
    db.session.delete(overview)
    db.session.commit()

    # Regenerate the department HTML after deletion
    department = Department.query.get(department_id)
    if department:
        generate_department_html(department)

    flash("Overview deleted successfully!", "success")
    return redirect(url_for('admin_department_overview'))


@app.route('/admin/delete_service/<int:id>', methods=['POST'])
def delete_service(id):
    service = DepartmentService.query.get_or_404(id)
    department_id = service.department_id
    db.session.delete(service)
    db.session.commit()

    # Regenerate the department HTML after deletion
    department = Department.query.get(department_id)
    if department:
        generate_department_html(department)

    flash("Service deleted successfully!", "success")
    return redirect(url_for('admin_department_services'))


# --- Utility function to generate HTML ---


@app.route('/debug-departments')
def debug_departments():
    rows = Department.query.all()
    return "<br>".join([f"ID={d.id}, Name={d.name}, Slug={d.slug}" for d in rows])


@app.route('/doctors/<slug>')
def doctor_detail(slug):
    doctor = Doctor.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Ensure correct image path
    if doctor.image_path:
        if doctor.image_path.startswith('doctors/'):
            img_file = doctor.image_path
        else:
            img_file = 'doctors/' + doctor.image_path
    else:
        img_file = 'doctors/dr-he.JPG'

    # Parse timings JSON
    try:
        doctor.timings_parsed = json.loads(
            doctor.timings) if doctor.timings else []
        # Collect all unique days across timings
        all_days = []
        for t in doctor.timings_parsed:
            if t.get("days"):
                all_days.extend(t["days"])
        doctor.days_parsed = list(dict.fromkeys(all_days))  # preserve order
    except Exception:
        doctor.timings_parsed = []
        doctor.days_parsed = []

    return render_template("doctor_detail.html", doctor=doctor, img_file=img_file)


app.secret_key = "your_secret_key_here"  # required for session


# --- login page ---
@app.route("/adx", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        emp_id = request.form.get("emp_id")  # changed from email
        password = request.form.get("password")

        # Basic validation
        if not emp_id or not password:
            flash("Please enter Employee ID and password", "warning")
            return redirect(url_for("admin_login"))

        # Fetch the user from DB using emp_id
        user = User.query.filter_by(emp_id=emp_id, is_active=True).first()

        if user and user.check_password(password):
            # Successful login
            session["admin_logged_in"] = True
            session["admin_id"] = user.id
            flash(f"Welcome {user.name}!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid Employee ID or password", "danger")
            return redirect(url_for("admin_login"))

    return render_template("admin/login.html")


# --- logout ---
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_id", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("admin_login"))


@app.route('/doctors')
def list_doctors():
    page = request.args.get('page', 1, type=int)
    per_page = 6

    pagination = (
        Doctor.query
        .filter_by(is_active=True)
        # strips "Dr. "
        .order_by(func.replace(func.lower(Doctor.name), "dr. ", ""))
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    for doctor in pagination.items:
        try:
            doctor.timings_parsed = json.loads(
                doctor.timings) if doctor.timings else []
        except Exception:
            doctor.timings_parsed = []

    return render_template(
        'doctors_list.html',
        doctors=pagination.items,
        pagination=pagination
    )


@app.route('/doctors/<slug>')
def doctor_profile(slug):
    # Fetch a single doctor by their unique slug
    doctor = Doctor.query.filter_by(slug=slug, is_active=True).first_or_404()
    # Pass the single doctor object to the profile template
    return render_template('doctor_profile.html', doctor=doctor)


@app.route('/admin/users', methods=['GET', 'POST'])
def admin_users():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        emp_id = request.form.get('emp_id')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        is_active = True if request.form.get('is_active') == 'on' else False

        # Access permissions
        permissions = {
            'banners': bool(request.form.get('banners')),
            'doctors': bool(request.form.get('doctors')),
            'counters': bool(request.form.get('counters')),
            'testimonials': bool(request.form.get('testimonials')),
            'specialities': bool(request.form.get('specialities')),
            'departments': bool(request.form.get('departments')),
            'health_packages': bool(request.form.get('health_packages')),
            'sports_packages': bool(request.form.get('sports_packages')),
            'department_content': bool(request.form.get('department_content')),
            'users': bool(request.form.get('users')),
            # Added
            'callback_requests': bool(request.form.get('callback_requests')),
            'reviews': bool(request.form.get('reviews')),
        }

        if user_id:  # Update existing user
            user = User.query.get(user_id)
            if user:
                user.emp_id = emp_id
                user.name = name
                user.email = email
                if password:
                    user.set_password(password)
                user.is_active = is_active

                # Update permissions
                if user.access:
                    for key, value in permissions.items():
                        setattr(user.access, key, value)
                else:
                    user.access = UserAccess(**permissions)
                db.session.commit()
                flash("User updated successfully!")
        else:  # Add new user
            new_user = User(emp_id=emp_id, name=name,
                            email=email, is_active=is_active)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()

            new_user.access = UserAccess(user_id=new_user.id, **permissions)
            db.session.add(new_user.access)
            db.session.commit()
            flash("User added successfully!")

        return redirect(url_for('admin_users'))

    users = User.query.all()

    # Convert access to dictionary for template usage
    users_data = []
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    for user in users:
        access_dict = {module: False for module in modules}
        if user.access:
            for module in modules:
                access_dict[module] = getattr(user.access, module, False)
        users_data.append({
            'id': user.id,
            'emp_id': user.emp_id,
            'name': user.name,
            'email': user.email,
            'is_active': user.is_active,
            'access': access_dict
        })

    return render_template('admin/users.html', users=users_data)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.access:
        db.session.delete(user.access)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!")
    return redirect(url_for('admin_users'))


@app.route('/request_callback', methods=['POST'])
def request_callback():
    try:
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone')
        package_name = data.get('package_name')

        if not name or not phone or not package_name:
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

        # Save to database
        callback = CallbackRequest(
            name=name, phone=phone, package_name=package_name)
        db.session.add(callback)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Callback request submitted successfully!'})
    except Exception:
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Something went wrong'}), 500


@app.route('/admin/callbacks')
def admin_callbacks():
    package_type = request.args.get(
        'package_type', 'health')  # 'health' or 'sports'
    package_title = request.args.get('package', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    callbacks = CallbackRequest.query

    if package_title:
        callbacks = callbacks.filter_by(package_name=package_title)

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        callbacks = callbacks.filter(CallbackRequest.created_at >= start_dt)

    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        callbacks = callbacks.filter(CallbackRequest.created_at <= end_dt)

    callbacks = callbacks.order_by(CallbackRequest.created_at.desc()).all()

    # Get packages for dropdown based on type
    if package_type == 'health':
        packages = HealthPackage.query.filter_by(is_active=True).all()
    else:
        packages = SportsPackage.query.filter_by(is_active=True).all()

    return render_template('admin/admin_callbacks.html', callbacks=callbacks, packages=packages, package_type=package_type)


@app.route('/admin/callbacks/download')
def download_callbacks():
    package_title = request.args.get('package', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    callbacks = CallbackRequest.query

    if package_title:
        callbacks = callbacks.filter_by(package_name=package_title)

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        callbacks = callbacks.filter(CallbackRequest.created_at >= start_dt)

    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        callbacks = callbacks.filter(CallbackRequest.created_at <= end_dt)

    callbacks = callbacks.order_by(CallbackRequest.created_at.desc()).all()

    data = [{
        'Name': c.name,
        'Phone': c.phone,
        'Package Name': c.package_name,
        'Requested At': c.created_at
    } for c in callbacks]

    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return send_file(
        output,
        download_name="callback_requests.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route("/submit-review", methods=["POST"])
def submit_review():
    name = request.form.get("reviewer-name")
    mobile_number = request.form.get("reviewer-number")
    email = request.form.get("reviewer-email")
    message = request.form.get("review-message")

    new_review = ReviewMessage(
        name=name,
        mobile_number=mobile_number,
        email=email,
        message=message
    )
    db.session.add(new_review)
    db.session.commit()

    flash("Your message has been submitted successfully!", "success")
    return redirect(url_for("thank_you"))


@app.route("/thank-you")
def thank_you():
    return "<h2>Thank you for your message. Management will get back to you soon.</h2>"

# Simple Admin Page


@app.route("/admin/reviews")
def admin_reviews():
    reviews = ReviewMessage.query.order_by(
        ReviewMessage.created_at.desc()).all()
    return render_template("admin/admin_reviews.html", reviews=reviews)


@app.route("/admin/reviews/export")
def export_reviews():
    reviews = ReviewMessage.query.order_by(
        ReviewMessage.created_at.desc()).all()

    # Convert to DataFrame
    data = [{
        "ID": r.id,
        "Date": r.created_at.strftime("%Y-%m-%d %H:%M"),
        "Name": r.name,
        "Mobile": r.mobile_number,
        "Email": r.email,
        "Message": r.message
    } for r in reviews]

    df = pd.DataFrame(data)

    # Save to BytesIO buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Messages")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="review_messages.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# admin routes end -------------------------------------------------------------------------------------------------------------------------
migrate = Migrate(app, db)

if __name__ == "__main__":
    try:
        with app.app_context():
            db.create_all()
            create_upload_dirs()
    except Exception as e:
        print("Startup error:", e)
        traceback.print_exc()

    app.run(host="0.0.0.0", port=8000, debug=True)
