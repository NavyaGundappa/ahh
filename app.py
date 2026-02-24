from sqlalchemy import func
import pandas as pd
from flask import request, redirect, url_for, flash, render_template, send_from_directory
import json
from flask_migrate import Migrate
from datetime import datetime
from flask import request, send_file, render_template
from io import BytesIO
from flask import Flask, render_template, send_file
from flask import request, redirect, url_for, flash, render_template, jsonify
import tempfile
import zipfile
from sqlalchemy.exc import IntegrityError
from flask import flash, redirect, url_for, render_template, request
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import pyodbc
from sqlalchemy.orm import load_only
from datetime import datetime, timedelta, time
from flask_httpauth import HTTPBasicAuth
from flask_caching import Cache
from werkzeug.security import generate_password_hash, check_password_hash
import traceback
import flash
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from models import db, Banner, Doctor, Counter, Testimonial, Speciality, Department,  HealthPackage, SportsPackage, DepartmentOverview, DepartmentService, User, UserAccess, CallbackRequest, ReviewMessage, Blog, BMWReportPDF, FAQ, DepartmentTestimonial, LifeMoment, Guide
from config import Config
import os
from functools import wraps
import io
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config.from_object(Config)
db.init_app(app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

GENERATED_BLOG_FOLDER = os.path.join(app.root_path, 'templates', 'blog_pages')
cache = Cache(config={'CACHE_TYPE': 'SimpleCache',
              'CACHE_DEFAULT_TIMEOUT': 300})
cache.init_app(app)

if not os.path.exists(GENERATED_BLOG_FOLDER):
    os.makedirs(GENERATED_BLOG_FOLDER)


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
@cache.cached(timeout=3600)
def index():
    banners = Banner.query.filter_by(is_active=True).order_by(
        Banner.created_at.desc()).all()
    doctors = Doctor.query.filter_by(is_active=True).all()
    counters = Counter.query.filter_by(is_active=True).all()
    testimonials = Testimonial.query.filter_by(is_active=True).options(
        joinedload(Testimonial.doctor)
    ).order_by(Testimonial.created_at.desc()).all()

    life_moments = LifeMoment.query.filter_by(
        is_active=True).options(
            joinedload(LifeMoment.doctor1),
            joinedload(LifeMoment.doctor2)
    ).order_by(LifeMoment.created_at.desc()).all()

    for moment in life_moments:
        if moment.video_link:
            moment.video_id = get_youtube_id(moment.video_link)

    processed_testimonials = []
    for t in testimonials:
        t.video_id = get_youtube_id(t.youtube_link)
        processed_testimonials.append(t)

    # Add this line to get specialities/departments
    specialities = Speciality.query.filter_by(
        is_active=True).order_by(Speciality.name).all()

    return render_template('index.html',
                           banners=banners,
                           doctors=doctors,
                           counters=counters,
                           testimonials=testimonials,
                           specialities=specialities, life_moments=life_moments)  # Add this parameter


@app.route('/appointments')
def appointments():
    return render_template('appointments.html')


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


@app.route('/best-plastic-surgeon-in-bangalore')
def expert_plastic_surgery():
    doctors = Doctor.query.filter_by(is_active=True).all()

    testimonials = Testimonial.query.filter_by(is_active=True).options(
        joinedload(Testimonial.doctor)
    ).order_by(Testimonial.created_at.desc()).all()

    blogs = Blog.query.filter_by(is_active=True)\
        .order_by(Blog.created_at.desc())\
        .limit(5)\
        .all()

    return render_template(
        'seopages/expert-plastic-surgery-in-bangalore.html',
        doctors=doctors,
        testimonials=testimonials,
        blogs=blogs
    )


@app.route('/best-ent-surgeon-in-bangalore')
def best_ent_surgeon():
    doctors = Doctor.query.filter_by(is_active=True).all()

    testimonials = Testimonial.query.filter_by(is_active=True).options(
        joinedload(Testimonial.doctor)
    ).order_by(Testimonial.created_at.desc()).all()

    blogs = Blog.query.filter_by(is_active=True)\
        .order_by(Blog.created_at.desc())\
        .limit(5)\
        .all()

    return render_template(
        'seopages/best-ent-surgeon-in-bangalore.html',
        doctors=doctors,
        testimonials=testimonials,
        blogs=blogs
    )


@app.route('/best-hospital-in-bellandur-bangalore')
def hospital_in_bellandur():
    doctors = Doctor.query.filter_by(is_active=True).all()

    testimonials = Testimonial.query.filter_by(is_active=True).options(
        joinedload(Testimonial.doctor)
    ).order_by(Testimonial.created_at.desc()).all()

    blogs = Blog.query.filter_by(is_active=True)\
        .order_by(Blog.created_at.desc())\
        .limit(5)\
        .all()

    departments = Department.query.filter_by(is_active=True)\
        .order_by(Department.name)\
        .all()

    return render_template(
        'seopages/best-hospital-in-bellandur-bangalore.html',
        doctors=doctors,
        testimonials=testimonials,
        blogs=blogs,
        departments=departments
    )

@app.route('/best-hospital-in-hosa-road-bangalore')
def hospital_in_hosa_road():
    doctors = Doctor.query.filter_by(is_active=True).all()

    testimonials = Testimonial.query.filter_by(is_active=True).options(
        joinedload(Testimonial.doctor)
    ).order_by(Testimonial.created_at.desc()).all()

    blogs = Blog.query.filter_by(is_active=True)\
        .order_by(Blog.created_at.desc())\
        .limit(5)\
        .all()

    departments = Department.query.filter_by(is_active=True)\
        .order_by(Department.name)\
        .all()

    return render_template(
        'seopages/best-hospital-in-hosa-road-bangalore.html',
        doctors=doctors,
        testimonials=testimonials,
        blogs=blogs,
        departments=departments
    )

@app.route('/best-hospital-in-sarjapur-road-bangalore')
def hospital_in_sarjapur_road():
    doctors = Doctor.query.filter_by(is_active=True).all()

    testimonials = Testimonial.query.filter_by(is_active=True).options(
        joinedload(Testimonial.doctor)
    ).order_by(Testimonial.created_at.desc()).all()

    blogs = Blog.query.filter_by(is_active=True)\
        .order_by(Blog.created_at.desc())\
        .limit(5)\
        .all()

    departments = Department.query.filter_by(is_active=True)\
        .order_by(Department.name)\
        .all()

    return render_template(
        'seopages/best-hospital-in-sarjapur-road-bangalore.html',
        doctors=doctors,
        testimonials=testimonials,
        blogs=blogs,
        departments=departments
    )


@app.route('/best-hospital-in-hsr-bangalore')
def hospital_in_hsr():
    doctors = Doctor.query.filter_by(is_active=True).all()

    testimonials = Testimonial.query.filter_by(is_active=True).options(
        joinedload(Testimonial.doctor)
    ).order_by(Testimonial.created_at.desc()).all()

    blogs = Blog.query.filter_by(is_active=True)\
        .order_by(Blog.created_at.desc())\
        .limit(5)\
        .all()

    departments = Department.query.filter_by(is_active=True)\
        .order_by(Department.name)\
        .all()

    return render_template(
        'seopages/best-hospital-in-hsr-bangalore.html',
        doctors=doctors,
        testimonials=testimonials,
        blogs=blogs,
        departments=departments
    )


@app.route('/best-hospital-in-electronic-city-bangalore')
def hospital_in_electronic_city():
    doctors = Doctor.query.filter_by(is_active=True).all()

    testimonials = Testimonial.query.filter_by(is_active=True).options(
        joinedload(Testimonial.doctor)
    ).order_by(Testimonial.created_at.desc()).all()

    blogs = Blog.query.filter_by(is_active=True)\
        .order_by(Blog.created_at.desc())\
        .limit(5)\
        .all()

    departments = Department.query.filter_by(is_active=True)\
        .order_by(Department.name)\
        .all()

    return render_template(
        'seopages/best-hospital-in-electronic-city-bangalore.html',
        doctors=doctors,
        testimonials=testimonials,
        blogs=blogs,
        departments=departments
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_name):
    """
    Decorator to check if a user has a specific permission.
    e.g., @permission_required('banners')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First, check if user is logged in at all
            if "admin_id" not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("admin_login"))

            # Get the user and their permissions
            user_id = session.get("admin_id")
            user = User.query.get(user_id)

            # Check if user exists and has access rights
            if not user or not user.access:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('admin_dashboard'))

            # The actual permission check
            # This checks if user.access.banners (or whatever permission_name is) is True
            has_permission = getattr(user.access, permission_name, False)

            if not has_permission:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('admin_dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/admin/get_doctor/<int:id>')
@login_required
@permission_required('doctors')
def get_doctor(id):
    try:
        doctor = Doctor.query.get_or_404(id)

        # Parse timings safely
        timings = []
        if doctor.timings:
            try:
                timings = json.loads(doctor.timings)
            except json.JSONDecodeError:
                timings = []

        return jsonify({
            "id": doctor.id,
            "name": doctor.name or "",
            "specialization": doctor.specialization or "",
            "designation": doctor.designation or "",
            "experience": doctor.experience or "",
            "languages": doctor.languages or "",
            "qualification": doctor.qualification or "",
            "appointment_link": doctor.appointment_link or "",
            "department_slug": doctor.department_slug or "",
            "slug": doctor.slug or "",
            "field_of_expertise": doctor.field_of_expertise or "",
            "overview": doctor.overview or "",
            "bio": doctor.bio or "",
            "fellowship_membership": doctor.fellowship_membership or "",
            "fellowship_links": doctor.fellowship_links or "",
            "talks_and_publications": doctor.talks_and_publications or "",
            "talks_links": doctor.talks_links or "",
            "image_path": doctor.image_path or "",
            "timings": timings
        })
    except Exception as e:
        print(f"Error in get_doctor route: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        flash("Please login first!", "warning")
        return redirect(url_for("admin_login"))

    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)

    # If the user is somehow invalid, redirect to login
    if not user:
        flash("Could not find user. Please log in again.", "warning")
        return redirect(url_for("admin_login"))

    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews', 'blogs', 'bmw_report', 'life_moments', 'guides']

    access = {module: False for module in modules}
    if user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    # FIX: Pass the `user` object to the template, which expects `current_user`
    return render_template("admin/dashboard.html", access=access, current_user=user)


@app.route('/admin/banners', methods=['GET', 'POST'])
@login_required
@permission_required('banners')
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
            button_text = request.form.get('button_text')
            button_link = request.form.get('button_link')

            # Save to DB
            banner = Banner(
                title=title,
                # This will be used in templates like <img src="{{ url_for('static', filename='img/' + banner.image_path) }}">
                image_path=db_path,
                alt_text=alt_text,
                button_text=button_text,  # <-- ADD THIS
                button_link=button_link

            )
            db.session.add(banner)
            db.session.commit()
            flash('Banner added successfully!')
            return redirect(url_for('admin_banners'))

    # Fetch banners for display
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews''blog', 'bmw_report', 'life_moments', 'guides']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    return render_template('admin/banners.html', banners=banners, access=access, current_user=user)


@app.route('/admin/guides', methods=['GET', 'POST'])
@login_required
# @permission_required('guides')
def admin_guides():
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content',
               'users', 'callback_requests', 'reviews', 'blogs', 'bmw_report', 'life_moments',
               'guides']

    # Handle POST requests
    if request.method == 'POST':
        # --- Handle Delete ---
        if 'delete_id' in request.form:
            guide_id = request.form.get('delete_id')
            guide = Guide.query.get_or_404(guide_id)

            # Clean up images
            for img_path in [guide.header_image_path, guide.content_image_path]:
                if img_path:
                    full_path = os.path.join(app.static_folder, img_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)

            db.session.delete(guide)
            db.session.commit()
            flash('Guide deleted successfully!', 'success')
            return redirect(url_for('admin_guides'))

        # --- Handle Add / Update ---
        guide_id = request.form.get('guide_id')
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')

        # Only process if we have title and content (basic validation)
        if title and content:
            # Ensure slug uniqueness
            if not slug:
                slug = title.lower().replace(' ', '-')

            original_slug = slug
            counter = 1
            query_filter = Guide.slug == slug
            if guide_id:
                query_filter = db.and_(
                    Guide.slug == slug, Guide.id != guide_id)

            while Guide.query.filter(query_filter).first():
                slug = f"{original_slug}-{counter}"
                counter += 1

            # Handle Header Image
            header_image_path = None
            if 'header_image' in request.files:
                file = request.files['header_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    folder = os.path.join(app.static_folder, 'img', 'guides')
                    os.makedirs(folder, exist_ok=True)
                    file.save(os.path.join(folder, filename))
                    header_image_path = f'img/guides/{filename}'

            # Handle Content Image
            content_image_path = None
            if 'content_image' in request.files:
                file = request.files['content_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    folder = os.path.join(app.static_folder, 'img', 'guides')
                    os.makedirs(folder, exist_ok=True)
                    file.save(os.path.join(folder, filename))
                    content_image_path = f'img/guides/{filename}'

            if guide_id:  # Update
                guide = Guide.query.get_or_404(guide_id)
                guide.title = title
                guide.slug = slug
                guide.content = content
                if header_image_path:
                    guide.header_image_path = header_image_path
                if content_image_path:
                    guide.content_image_path = content_image_path
                flash('Guide updated successfully!', 'success')
            else:  # Add
                guide = Guide(
                    title=title,
                    slug=slug,
                    content=content,
                    header_image_path=header_image_path,
                    content_image_path=content_image_path
                )
                db.session.add(guide)
                flash('Guide added successfully!', 'success')

            db.session.commit()
            return redirect(url_for('admin_guides'))
        else:
            flash('Title and Content are required!', 'danger')
            return redirect(url_for('admin_guides'))

    # GET request
    guides = Guide.query.order_by(Guide.created_at.desc()).all()

    # User Access for Sidebar
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    access = {module: getattr(user.access, module, False)
              for module in modules} if user and user.access else {}

    return render_template('admin/guides.html', guides=guides, access=access, current_user=user)


@app.route('/api/get_guide/<int:id>')
@login_required
def get_guide(id):
    try:
        guide = Guide.query.get_or_404(id)
        return jsonify({
            "id": guide.id,
            "title": guide.title,
            "slug": guide.slug,
            "content": guide.content,
            "header_image_path": guide.header_image_path,
            "content_image_path": guide.content_image_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/upload_ckeditor', methods=['POST'])
@login_required
def upload_ckeditor():
    file = request.files.get('upload')
    if file:
        filename = secure_filename(file.filename)
        # 1. Save to the correct physical path
        upload_folder = os.path.join(app.static_folder, 'uploads', 'ckeditor')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        # 2. Generate the URL (Absolute path)
        # Result: http://127.0.0.1:5000/static/uploads/ckeditor/filename.jpg
        file_url = url_for(
            'static', filename=f'uploads/ckeditor/{filename}', _external=True)

        return jsonify({
            "uploaded": 1,
            "fileName": filename,
            "url": file_url
        })
    return jsonify({"uploaded": 0, "error": {"message": "Upload failed"}})


@app.route('/api/toggle_guide/<int:id>', methods=['POST'])
def toggle_guide(id):
    guide = Guide.query.get_or_404(id)
    guide.is_active = not guide.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': guide.is_active})


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
        banner.button_text = request.form.get('button_text')
        banner.button_link = request.form.get('button_link')

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


def safe_int_or_none(value_str):
    """
    Safely converts a string from a form field to an integer or None.
    Handles None, empty string '', and '0' (common for 'Select...' options)
    as None, and catches ValueError on conversion attempt.
    """
    if not value_str or str(value_str).strip() in ('', '0'):
        return None
    try:
        return int(value_str.strip())
    except ValueError:
        return None


def get_youtube_id(link):
    if not link:
        return None

    link = link.strip()

    # Handle YouTube Shorts (Portrait videos) - ADD THIS BLOCK
    if 'shorts/' in link:
        return link.split('shorts/')[1].split('?')[0].split('&')[0]

    # Handle embed links
    if 'embed/' in link:
        return link.split('embed/')[1].split('?')[0].split('&')[0]

    # Handle watch links
    if 'watch?v=' in link:
        return link.split('watch?v=')[1].split('&')[0].split('?')[0]

    # Handle short links (youtu.be)
    if 'youtu.be/' in link:
        return link.split('youtu.be/')[1].split('&')[0].split('?')[0]

    return None


@app.route('/our-stories')  # Choose a descriptive URL
def our_stories():
    """
    Fetches all LifeMoment data, including doctor details, for the dedicated stories page.
    """

    initial_category = request.args.get('category_code', 'patient_stories')
    highlight_id = request.args.get('highlight_id')
    # Categories are needed to render the tabs
    categories = [
        ('patient_stories', 'Patient Stories'),
        ('doctors_speak', 'Doctors Speak'),
        ('general', 'General'),
        ('health_days', 'Health Days'),
        ('events', 'Events'),
        ('written_testimonial', 'Written Reviews')
    ]

    # Fetching the same data as the homepage's life_moments section
    life_moments = LifeMoment.query.filter_by(
        is_active=True).options(
            joinedload(LifeMoment.doctor1),
            joinedload(LifeMoment.doctor2)
    ).order_by(LifeMoment.created_at.desc()).all()

    for moment in life_moments:
        # Assuming get_youtube_id is defined and works as in your original route
        if moment.video_link:
            moment.video_id = get_youtube_id(moment.video_link)

    return render_template('life_at_glance.html',
                           life_moments=life_moments,
                           initial_category=initial_category,
                           highlight_id=highlight_id,
                           categories=categories)


@app.route('/admin/life_moments', methods=['GET', 'POST'])
@login_required
def admin_life_moments():
    if request.method == 'POST':
        # --- 1. Handle Delete ---
        if 'delete_id' in request.form:
            moment_id = request.form.get('delete_id')
            moment = LifeMoment.query.get_or_404(moment_id)

            # Delete image if exists
            if moment.image_path:
                try:
                    os.remove(os.path.join(
                        app.static_folder, moment.image_path))
                except:
                    # Ignore file not found errors during deletion
                    pass

            try:
                db.session.delete(moment)
                db.session.commit()
                flash('Item deleted successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('Error: Could not delete item due to a related record.', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(
                    f'An unexpected error occurred during deletion: {e}', 'danger')

            return redirect(url_for('admin_life_moments'))

        # --- 2. Handle Add/Update ---
        moment_id = request.form.get('moment_id')
        category = request.form.get('category')
        title = request.form.get('title')
        description = request.form.get('description')
        video_link = request.form.get('video_link')

        # *** MODIFIED: Use the robust conversion function for doctor IDs ***
        doctor1_id = safe_int_or_none(request.form.get('doctor1_id'))
        doctor2_id = safe_int_or_none(request.form.get('doctor2_id'))

        # Your previous manual try-except blocks are no longer needed
        # as they are replaced by the helper function.

        # Handle Image Upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            # Assuming allowed_file is defined and checks extension
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                folder = os.path.join(app.static_folder, 'img', 'life_moments')
                os.makedirs(folder, exist_ok=True)
                file.save(os.path.join(folder, filename))
                image_path = f'img/life_moments/{filename}'

        # *** MODIFIED: Wrap database commit in try/except for graceful error handling ***
        try:
            if moment_id:  # Edit
                moment = LifeMoment.query.get_or_404(moment_id)
                moment.category = category
                moment.title = title
                moment.description = description
                moment.video_link = video_link
                moment.doctor1_id = doctor1_id
                moment.doctor2_id = doctor2_id

                # Only update image path if a new image was uploaded
                if image_path:
                    moment.image_path = image_path

                db.session.commit()
                flash('Item updated successfully!', 'success')
            else:  # Add
                new_moment = LifeMoment(
                    category=category,
                    title=title,
                    description=description,
                    video_link=video_link,
                    image_path=image_path,
                    doctor1_id=doctor1_id,
                    doctor2_id=doctor2_id,
                )
                db.session.add(new_moment)
                db.session.commit()
                flash('Item added successfully!', 'success')

        except IntegrityError:
            db.session.rollback()
            # This handles NOT NULL constraints or invalid foreign keys (e.g., doctor ID)
            flash('Error: Could not save item. Ensure all required fields are filled and valid doctor IDs are selected.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred: {e}', 'danger')

        return redirect(url_for('admin_life_moments'))

    # --- GET Request (No change needed here) ---
    moments = LifeMoment.query.order_by(
        LifeMoment.category, LifeMoment.created_at.desc()).all()

    doctors = Doctor.query.filter_by(
        is_active=True).order_by(Doctor.name).all()

    # User Access (for sidebar)
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content',
               'users', 'callback_requests', 'reviews', 'blogs', 'bmw_report', 'life_moments']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    return render_template('admin/life_moments.html', moments=moments, access=access, current_user=user, doctors=doctors)


@app.route('/api/toggle_life_moment/<int:id>', methods=['POST'])
def toggle_life_moment(id):
    moment = LifeMoment.query.get_or_404(id)
    moment.is_active = not moment.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': moment.is_active})


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


def doctor_to_dict(doctor):
    """Convert Doctor object to JSON-serializable dictionary for template."""
    return {
        "id": doctor.id,
        "name": doctor.name,
        "specialization": doctor.specialization,
        "designation": doctor.designation,
        "experience": doctor.experience,
        "qualification": doctor.qualification,
        "languages": doctor.languages,
        "overview": doctor.overview,
        "fellowship_membership": doctor.fellowship_membership,
        "fellowship_links": doctor.fellowship_links,
        "fellowship_file_path": doctor.fellowship_file_path,
        "field_of_expertise": doctor.field_of_expertise,
        "talks_and_publications": doctor.talks_and_publications,
        "talks_links": doctor.talks_links,
        "talks_file_path": doctor.talks_file_path,
        "bio": doctor.bio,
        "image_path": doctor.image_path,
        "appointment_link": doctor.appointment_link,
        "department_slug": doctor.department_slug,
        "slug": doctor.slug,
        "timings": json.loads(doctor.timings) if doctor.timings else [],
        "days_parsed": getattr(doctor, 'days_parsed', [])
    }


def handle_file_upload(file, folder_name):
    """Handle file uploads for fellowships and talks."""
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        os.makedirs(folder_path, exist_ok=True)
        save_path = os.path.join(folder_path, filename)
        file.save(save_path)
        return f"img/{folder_name}/{filename}"
    return None

# --- Admin Doctors Route ---


@app.route('/admin/doctors', methods=['GET', 'POST'])
@login_required
@permission_required('doctors')
def admin_doctors():
    departments = Department.query.filter_by(is_active=True).all()

    # Handle search
    search_query = request.args.get('search', '').strip()

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'add':
            return add_doctor_function(request, departments)
        elif form_type == 'edit':
            return edit_doctor_function(request, departments)
        else:
            flash("Invalid form submission!", "danger")
            return redirect(url_for('admin_doctors'))

    # ----- GET Request: Fetch doctors with optional search -----
    doctors_query = Doctor.query

    if search_query:
        doctors_query = doctors_query.filter(
            db.or_(
                Doctor.name.ilike(f'%{search_query}%'),
                Doctor.specialization.ilike(f'%{search_query}%'),
                Doctor.department_slug.ilike(f'%{search_query}%'),
                Doctor.designation.ilike(f'%{search_query}%')
            )
        )

    doctors = doctors_query.order_by(
        Doctor.display_order.asc(), Doctor.name.asc()).all()
    doctors_json = [doctor_to_dict(d) for d in doctors]

    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    return render_template('admin/doctors.html',
                           doctors=doctors_json,
                           departments=departments,
                           access=access,
                           current_user=user,
                           search_query=search_query)


def add_doctor_function(request, departments):
    """Handle adding a new doctor."""
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
    time_from_hour = request.form.getlist('time_from_hour[]')
    time_from_minute = request.form.getlist('time_from_minute[]')
    time_from_period = request.form.getlist('time_from_period[]')
    time_to_hour = request.form.getlist('time_to_hour[]')
    time_to_minute = request.form.getlist('time_to_minute[]')
    time_to_period = request.form.getlist('time_to_period[]')

    timings_list = []
    for i in range(len(time_from_hour)):
        if time_from_hour[i] and time_to_hour[i]:
            days = request.form.getlist(f'days[{i}][]')
            # Format time as "HH:MM AM/PM"
            from_time = f"{time_from_hour[i]}:{time_from_minute[i]}"
            to_time = f"{time_to_hour[i]}:{time_to_minute[i]}"

            timings_list.append({
                "from_hour": time_from_hour[i],
                "from_minute": time_from_minute[i],
                "from_period": time_from_period[i],
                "to_hour": time_to_hour[i],
                "to_minute": time_to_minute[i],
                "to_period": time_to_period[i],
                "from": from_time,
                "to": to_time,
                "days": days
            })

    timings = json.dumps(timings_list) if timings_list else None

    # ----- Validation -----
    if not name or not specialization or not department_slug:
        flash("Name, Specialization, and Department are required!", "danger")
        return redirect(url_for('admin_doctors'))

    if not slug:
        slug = name.lower().replace(' ', '-')

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

    # ----- Calculate display order -----
    max_order = db.session.query(db.func.max(
        Doctor.display_order)).scalar() or 0
    display_order = max_order + 1

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
        timings=timings,
        display_order=display_order
    )
    db.session.add(doctor)
    db.session.commit()

    # Regenerate department HTML if needed
    department = Department.query.filter_by(slug=department_slug).first()
    if department:
        generate_department_html(department)

    flash('Doctor added successfully!', 'success')
    return redirect(url_for('admin_doctors'))


def edit_doctor_function(request, departments):
    """Handle editing an existing doctor."""
    doctor_id = request.form.get('doctor_id')
    doctor = Doctor.query.get_or_404(doctor_id)

    # ----- Collect basic form data -----
    doctor.name = request.form.get('name', '').strip()
    doctor.specialization = request.form.get('specialization', '').strip()
    doctor.designation = request.form.get('designation', '').strip()
    doctor.experience = request.form.get('experience', '').strip()
    doctor.languages = request.form.get('languages', '').strip()
    doctor.bio = request.form.get('bio', '').strip()
    doctor.qualification = request.form.get('qualification', '').strip()
    doctor.overview = request.form.get('overview', '').strip()
    doctor.fellowship_membership = request.form.get(
        'fellowship_membership', '').strip()
    doctor.fellowship_links = request.form.get('fellowship_links', '').strip()
    doctor.field_of_expertise = request.form.get(
        'field_of_expertise', '').strip()
    doctor.talks_and_publications = request.form.get(
        'talks_and_publications', '').strip()
    doctor.talks_links = request.form.get('talks_links', '').strip()
    doctor.appointment_link = request.form.get('appointment_link', '').strip()
    doctor.department_slug = request.form.get('department_slug', '').strip()
    doctor.slug = request.form.get('slug', '').strip()

    # ----- Collect timings with days -----
    time_from_hour = request.form.getlist('time_from_hour[]')
    time_from_minute = request.form.getlist('time_from_minute[]')
    time_from_period = request.form.getlist('time_from_period[]')
    time_to_hour = request.form.getlist('time_to_hour[]')
    time_to_minute = request.form.getlist('time_to_minute[]')
    time_to_period = request.form.getlist('time_to_period[]')

    timings_list = []
    for i in range(len(time_from_hour)):
        if time_from_hour[i] and time_to_hour[i]:
            days = request.form.getlist(f'days[{i}][]')
            # Format time as "HH:MM AM/PM"
            from_time = f"{time_from_hour[i]}:{time_from_minute[i]}"
            to_time = f"{time_to_hour[i]}:{time_to_minute[i]}"

            timings_list.append({
                "from_hour": time_from_hour[i],
                "from_minute": time_from_minute[i],
                "from_period": time_from_period[i],
                "to_hour": time_to_hour[i],
                "to_minute": time_to_minute[i],
                "to_period": time_to_period[i],
                "from": from_time,
                "to": to_time,
                "days": days
            })

    doctor.timings = json.dumps(timings_list) if timings_list else None

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

    # ----- Handle file uploads -----
    if 'fellowship_file' in request.files:
        fellowship_file = handle_file_upload(
            request.files['fellowship_file'], 'fellowships')
        if fellowship_file:
            doctor.fellowship_file_path = fellowship_file

    if 'talks_file' in request.files:
        talks_file = handle_file_upload(request.files['talks_file'], 'talks')
        if talks_file:
            doctor.talks_file_path = talks_file

    db.session.commit()

    # Regenerate department HTML if needed
    department = Department.query.filter_by(
        slug=doctor.department_slug).first()
    if department:
        generate_department_html(department)

    flash('Doctor updated successfully!', 'success')
    return redirect(url_for('admin_doctors'))


@app.route('/admin/delete_doctor/<int:doctor_id>')
@login_required
@permission_required('doctors')
def delete_doctor(doctor_id):
    """Delete a doctor."""
    doctor = Doctor.query.get_or_404(doctor_id)
    department_slug = doctor.department_slug

    db.session.delete(doctor)
    db.session.commit()

    # Regenerate department HTML if needed
    department = Department.query.filter_by(slug=department_slug).first()
    if department:
        generate_department_html(department)

    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('admin_doctors'))
# Add this route to handle the drag-and-drop order updates


@app.route('/admin/doctors/update-order', methods=['POST'])
@login_required
@permission_required('doctors')
def update_doctors_orders():
    try:
        data = request.get_json()
        order_data = data.get('order', [])

        for doctor_data in order_data:
            doctor_id = doctor_data['id']
            display_order = doctor_data['display_order']

            # Update the doctor's display_order in the database
            doctor = Doctor.query.get(doctor_id)
            if doctor:
                doctor.display_order = display_order

        db.session.commit()
        return jsonify({'success': True, 'message': 'Doctor order updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


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
    except Exception:
        doctor.timings_parsed = []

    return render_template('admin/doctors.html', doctor=doctor, departments=departments, doctors=Doctor.query.all())


def _fetch_department_data(department):
    """
    Fetches all necessary data objects for rendering a department page.

    This function consolidates the queries to avoid duplication in 
    the department view route and the HTML generation function.
    """

    # 1. Overview
    overview = DepartmentOverview.query.filter_by(
        department_id=department.id).first()

    # 2. Services
    services = DepartmentService.query.filter_by(
        department_id=department.id, is_active=True).all()

    # 3. Doctors
    doctors = Doctor.query.filter_by(
        department_slug=department.slug, is_active=True).all()

    # 4. Testimonials
    testimonials = DepartmentTestimonial.query.filter_by(
        department_id=department.id, is_active=True
    ).order_by(DepartmentTestimonial.display_order, DepartmentTestimonial.created_at.desc()).all()

    # 5. FAQs
    faqs = FAQ.query.filter_by(
        department_id=department.id, is_active=True
    ).order_by(FAQ.display_order, FAQ.created_at.desc()).all()

    # 6. Blogs
    blogs = Blog.query.filter_by(
        department_id=department.id, is_active=True
    ).order_by(Blog.created_at.desc()).limit(6).all()

    # 7. All Departments (for navigation/carousel)
    all_departments = Department.query.filter_by(
        is_active=True).order_by(Department.name).all()

    # Return a dictionary of all the context variables
    return {
        'department': department,
        'overview': overview,
        'services': services,
        'doctors': doctors,
        'testimonials': testimonials,
        'faqs': faqs,
        'blogs': blogs,
        'departments': all_departments,  # Renamed to 'departments' for template clarity
    }

# --- Utility function to generate HTML ---


def generate_department_html(department):
    """
    Generates or regenerates the static HTML file for the given department.
    This function should be called by administrative endpoints after content updates.
    """
    try:
        # Use the reusable helper to get all necessary data
        context = _fetch_department_data(department)

        # Determine which template to use (e.g., department.html)
        # Note: You need a way to render a template to a string.
        # This often involves importing 'app' (the Flask instance) and
        # using app.test_client().get('/') or using Jinja's environment directly.

        # --- PLACEHOLDER FOR ACTUAL HTML CACHING LOGIC ---
        # The key takeaway is to use the helper function:
        # html_content = render_template('department.html', **context)
        # with open(f'/path/to/static/departments/{department.slug}.html', 'w') as f:
        #     f.write(html_content)

        print(f"Successfully generated static content for: {department.slug}")
        # --- END PLACEHOLDER ---

    except Exception as e:
        print(f"Error generating HTML for {department.slug}: {e}")


@app.route('/admin/counters', methods=['GET', 'POST'])
@login_required
@permission_required('counters')
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
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)
    return render_template('admin/counters.html', counters=counters, access=access, current_user=user)


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
@login_required
@permission_required('testimonials')
def admin_testimonials():
    # --- POST REQUEST (Adding data) ---
    if request.method == 'POST':
        patient_name = request.form.get('patient_name')
        content = request.form.get('content')
        doctor1_id = request.form.get('doctor1_id')
        doctor2_id = request.form.get('doctor2_id')

        # --- NEW: Get YouTube Link ---
        youtube_link = request.form.get('youtube_link', '').strip()

        # Convert to embed format if needed
        if youtube_link:
            if "watch?v=" in youtube_link:
                youtube_link = youtube_link.replace("watch?v=", "embed/")
            elif "youtu.be/" in youtube_link:
                youtube_link = youtube_link.replace(
                    "youtu.be/", "www.youtube.com/embed/")
        # -----------------------------

        if not patient_name or not content or not doctor1_id:
            flash('Patient Name, Content, and Primary Doctor are required', 'danger')
            return redirect(request.url)

        testimonial = Testimonial(
            patient_name=patient_name,
            content=content,
            youtube_link=youtube_link,
            doctor_id=int(doctor1_id),
            doctor2_id=int(doctor2_id) if doctor2_id else None
        )

        db.session.add(testimonial)
        db.session.commit()
        flash('Testimonial added successfully!', 'success')
        return redirect(url_for('admin_testimonials'))

    # --- GET REQUEST (Rendering the page) ---
    # This part was likely missing or indented incorrectly causing the error
    testimonials = Testimonial.query.order_by(
        Testimonial.created_at.desc()).all()
    doctors = Doctor.query.filter_by(
        is_active=True).order_by(Doctor.name).all()

    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)

    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages',
               'department_content', 'users', 'callback_requests', 'reviews',
               'blogs', 'bmw_report', 'life_moments']

    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    return render_template(
        'admin/testimonials.html',
        testimonials=testimonials,
        doctors=doctors,
        access=access,
        current_user=user
    )


@app.route('/admin/testimonials/edit/<int:testimonial_id>', methods=['POST'])
@login_required
@permission_required('testimonials')
def edit_testimonial(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)

    patient_name = request.form.get('patient_name')
    content = request.form.get('content')
    doctor1_id = request.form.get('doctor1_id')
    doctor2_id = request.form.get('doctor2_id')

    # --- NEW: Get YouTube Link ---
    youtube_link = request.form.get('youtube_link', '').strip()

    # Convert to embed format if needed
    if youtube_link and "watch?v=" in youtube_link:
        youtube_link = youtube_link.replace("watch?v=", "embed/")
    elif youtube_link and "youtu.be/" in youtube_link:
        youtube_link = youtube_link.replace(
            "youtu.be/", "www.youtube.com/embed/")
    # -----------------------------

    if not patient_name or not content or not doctor1_id:
        flash('Patient Name, Content, and Primary Doctor are required', 'danger')
        return redirect(url_for('admin_testimonials'))

    testimonial.patient_name = patient_name
    testimonial.content = content
    testimonial.youtube_link = youtube_link  # <--- Update it here
    testimonial.doctor_id = int(doctor1_id)
    testimonial.doctor2_id = int(doctor2_id) if doctor2_id else None

    db.session.commit()  # Removed db.session.expire(testimonial) as commit handles it
    flash('Testimonial updated successfully!', 'success')
    return redirect(url_for('admin_testimonials'))


@app.route('/admin/testimonials/delete/<int:testimonial_id>', methods=['POST'])
def delete_testimonial(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)

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
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)
    return render_template('admin/specialities.html', specialities=specialities, access=access, current_user=user)


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
            department.specialists_heading = request.form.get(
                'specialists_heading')
            department.specialists_content = request.form.get(
                'specialists_content')
            department.meta_title = request.form.get('meta_title')
            department.meta_description = request.form.get('meta_description')
            department.canonical_url = request.form.get('canonical_url')

            # ✅ New field for banner alt text
            department.banner_alt_text = request.form.get('banner_alt_text')

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

            # ✅ Regenerate department HTML after update
            generate_department_html(department)

            flash("Department updated successfully!", "success")
            return redirect(url_for('admin_departments'))

        # ------------------ ADD NEW DEPARTMENT ------------------
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description')
        specialists_heading = request.form.get('specialists_heading')
        specialists_content = request.form.get('specialists_content')

        meta_title = request.form.get('meta_title')
        meta_description = request.form.get('meta_description')
        canonical_url = request.form.get('canonical_url')

        # ✅ New field for alt text
        banner_alt_text = request.form.get('banner_alt_text')

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

        # ✅ Create and save department
        department = Department(
            name=name,
            slug=slug,
            description=description,
            specialists_heading=specialists_heading,
            specialists_content=specialists_content,
            meta_title=meta_title,
            meta_description=meta_description,
            canonical_url=canonical_url,
            icon_path=icon_path,
            banner_path=banner_path,
            banner_alt_text=banner_alt_text  # ✅ New field
        )

        db.session.add(department)
        db.session.commit()

        # ✅ Regenerate department HTML after creation
        generate_department_html(department)

        flash("Department added successfully!", "success")
        return redirect(url_for('admin_departments'))

    # ------------------ GET DEPARTMENTS ------------------
    departments = Department.query.order_by(Department.name).all()
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)
    return render_template('admin/departments.html', departments=departments, access=access, current_user=user)

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
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)
    return render_template('admin/health-packages.html', packages=packages, access=access, current_user=user)


@app.route('/api/toggle_package/<int:package_id>', methods=['POST'])
def toggle_package(package_id):
    package = HealthPackage.query.get_or_404(package_id)
    package.is_active = not package.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': package.is_active})

# healthpackage end

# sportspackage start


@app.route('/test')
def test():
    return render_template('test.html')


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
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)
    return render_template('admin/sports_package.html', packages=packages, access=access, current_user=user)


@app.route('/api/toggle_sports_package/<int:package_id>', methods=['POST'])
def toggle_sports_package(package_id):
    package = SportsPackage.query.get_or_404(package_id)
    package.is_active = not package.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': package.is_active})
# sportspackage end


@app.route('/departments/<slug>')
def department_page(slug):
    """
    Renders the dynamic department page.
    """
    # 1. Fetch the department object (first to handle 404)
    department = Department.query.filter_by(
        slug=slug, is_active=True).first_or_404()

    # 2. Use the reusable helper to fetch all related content
    context = _fetch_department_data(department)

    # 3. Check for custom template
    template_path = f"departments/{slug}.html"
    if os.path.exists(os.path.join(app.template_folder, template_path)):
        # If custom template exists, render it using the unpacked context dictionary
        return render_template(template_path, **context)
    # 4. Render the default template using the unpacked context dictionary
    return render_template("department.html", **context)

# ------------------ ADMIN: Department Overview ------------------


@app.route('/admin/department_overview', methods=['GET', 'POST'])
@login_required
@permission_required('department_content')
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

    # Get all data for the template
    overviews = DepartmentOverview.query.all()
    department_testimonials = DepartmentTestimonial.query.order_by(
        DepartmentTestimonial.display_order, DepartmentTestimonial.created_at.desc()).all()
    faqs = FAQ.query.order_by(FAQ.display_order, FAQ.created_at.desc()).all()
    departments = Department.query.all()

    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content',
               'users', 'callback_requests', 'reviews', 'blogs', 'bmw_report', 'life_moments']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    return render_template("admin/department_overview.html",
                           overviews=overviews,
                           department_testimonials=department_testimonials,  # Fixed variable name
                           faqs=faqs,
                           departments=departments,
                           access=access,
                           current_user=user)


# ------------------ ADMIN: Department Services ------------------
@app.route('/admin/department_services', methods=['GET', 'POST'])
def admin_department_services():
    if request.method == 'POST':
        # Check if it's a services overview update
        if 'services_overview' in request.form:
            service_id = request.form.get('service_id')
            services_overview = request.form.get('services_overview')

            service = DepartmentService.query.get_or_404(service_id)
            service.services_overview = services_overview
            db.session.commit()

            # Regenerate department HTML
            department = Department.query.get(service.department_id)
            if department:
                generate_department_html(department)
            flash("Services overview updated successfully!", "success")
            return redirect(url_for('admin_department_services'))

        # Existing service management code
        service_id = request.form.get('service_id')
        department_id = request.form.get('department_id')

        if service_id:  # UPDATE
            service = DepartmentService.query.get_or_404(service_id)
            service.title = request.form.get('title')
            service.description = request.form.get('description')
            service.list_items = request.form.get('list_items')
            service.services_overview = request.form.get('services_overview')
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
                services_overview=request.form.get('services_overview'),
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
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)
    return render_template("admin/department_services.html", services=services, departments=departments, access=access, current_user=user)


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


@app.route('/admin/doctors/update-order', methods=['POST'])
def update_doctors_order():
    try:
        data = request.get_json()
        order_data = data.get('order', [])

        for doctor_data in order_data:
            doctor_id = doctor_data['id']
            display_order = doctor_data['display_order']

            # Update the doctor's display_order in the database
            doctor = Doctor.query.get(doctor_data['id'])
            if doctor:
                doctor.display_order = display_order

        db.session.commit()
        return jsonify({'success': True, 'message': 'Doctor order updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/doctors')
def list_doctors():
    page = request.args.get('page', 1, type=int)
    per_page = 6

    pagination = (
        Doctor.query
        .filter_by(is_active=True)
        .order_by(Doctor.display_order.asc())  # Add this line
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


@app.route("/admin/users", methods=["GET", "POST"])
@login_required
@permission_required("users")
def admin_users():

    modules = [
        "banners", "doctors", "counters", "testimonials", "specialities",
        "departments", "health_packages", "sports_packages", "department_content",
        "users", "callback_requests", "reviews", "blogs", "bmw_report", "life_moments"
    ]

    if request.method == "POST":
        user_id = request.form.get("user_id")
        emp_id = request.form.get("emp_id")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        is_active = request.form.get("is_active") == 'on'

        # Add validation
        if not emp_id or not name or not email:
            flash("Emp ID, Name, and Email are required!", "danger")
            return redirect(url_for("admin_users"))

        user = None
        if user_id:
            # Update existing user
            user = User.query.get(user_id)
            if user:
                user.emp_id = emp_id
                user.name = name
                user.email = email
                if password and password.strip():  # Only update password if provided
                    user.password_hash = generate_password_hash(password)
                user.is_active = is_active
                flash("User updated successfully!", "success")
            else:
                flash("User not found!", "danger")
                return redirect(url_for("admin_users"))
        else:
            # Create new user
            if not password:
                flash("Password is required for a new user!", "danger")
                return redirect(url_for("admin_users"))

            # Check for duplicate email
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("A user with that email already exists.", "danger")
                return redirect(url_for("admin_users"))

            # Check for duplicate emp_id
            existing_emp = User.query.filter_by(emp_id=emp_id).first()
            if existing_emp:
                flash("A user with that Employee ID already exists.", "danger")
                return redirect(url_for("admin_users"))

            user = User(
                emp_id=emp_id,
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                is_active=is_active
            )
            db.session.add(user)
            db.session.flush()  # Get user.id for UserAccess
            flash("User added successfully!", "success")

        # Handle permissions - FIXED LOGIC
        if user:
            # Get or create user access
            user_access = UserAccess.query.filter_by(user_id=user.id).first()
            if not user_access:
                user_access = UserAccess(user_id=user.id)
                db.session.add(user_access)

            # Update each permission
            for module in modules:
                is_checked = request.form.get(module) == 'on'
                setattr(user_access, module, is_checked)

        db.session.commit()
        return redirect(url_for("admin_users"))

    # GET REQUEST - FIXED LOGIC
    users = User.query.order_by(User.created_at.desc()).all()

    # Process users with their access permissions
    users_with_access = []
    for user in users:
        access_dict = {}
        for module in modules:
            # Check if user has access record and get permission
            if user.access:
                access_dict[module] = getattr(user.access, module, False)
            else:
                access_dict[module] = False

        users_with_access.append({
            'id': user.id,
            'emp_id': user.emp_id,
            'name': user.name,
            'email': user.email,
            'is_active': user.is_active,
            'access': access_dict
        })

    # Get current admin user for sidebar
    admin_id = session.get("admin_id")
    current_admin = User.query.get(admin_id)

    if not current_admin:
        flash("Could not find user. Please log in again.", "warning")
        return redirect(url_for("admin_login"))

    # Get current admin's access for sidebar
    current_access = {module: False for module in modules}
    if current_admin.access:
        for module in modules:
            current_access[module] = getattr(
                current_admin.access, module, False)

    return render_template('admin/users.html',
                           users=users_with_access,
                           modules=modules,
                           access=current_access,
                           current_user=current_admin)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.access:
        db.session.delete(user.access)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!")
    return redirect(url_for('admin_users'))


@app.route('/request_callback/', methods=['POST'])
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
@login_required
@permission_required('callback_requests')
def admin_callbacks():
    # 1. Capture the form data from the URL
    package_type = request.args.get('package_type', '')
    specific_package_id = request.args.get('package', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # 2. Start the base query
    query = CallbackRequest.query

    # 3. Filter by Package Type (Health vs Sports)
    # We check if 'Health' or 'Sports' is in the package_name string
    if package_type == 'health':
        query = query.filter(CallbackRequest.package_name.ilike('%health%'))
    elif package_type == 'sports':
        query = query.filter(CallbackRequest.package_name.ilike('%sports%'))

    # 4. Filter by Date Range
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(CallbackRequest.created_at >= start_dt)

    if end_date:
        # We add 1 day to the end date to include all requests from that specific day
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(CallbackRequest.created_at < end_dt)

    # 5. Execute query and order by latest first
    callbacks = query.order_by(CallbackRequest.created_at.desc()).all()

    # 6. Fetch packages for the dropdown list (to populate the "Package" select)
    all_packages = HealthPackage.query.all() + SportsPackage.query.all()

    # Required sidebar/access data for your template
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'users', 'callback_requests']
    access = {m: getattr(user.access, m, False)
              for m in modules if user.access}

    return render_template('admin/admin_callbacks.html',
                           callbacks=callbacks,
                           packages=all_packages,  # Passes the package list to HTML
                           access=access,
                           current_user=user)


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


@app.route("/admin/reviews")
@login_required
@permission_required('reviews')
def admin_reviews():
    reviews = ReviewMessage.query.order_by(
        ReviewMessage.created_at.desc()).all()
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)

    # If the user is somehow invalid, redirect to login
    if not user:
        flash("Could not find user. Please log in again.", "warning")
        return redirect(url_for("admin_login"))

    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']

    access = {module: False for module in modules}
    if user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content', 'users', 'callback_requests', 'reviews']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)
    return render_template("admin/admin_reviews.html", reviews=reviews, access=access, current_user=user)


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


@app.route('/blog')
def blog():
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('blog.html', departments=departments)


@app.route('/api/blogs')
def api_blogs():
    try:
        department_slug = request.args.get('department', 'all')
        search_query = request.args.get('search', '')

        # Base query for active blogs
        blog_query = Blog.query.filter_by(is_active=True)

        # Filter by department if specified
        if department_slug != 'all':
            department = Department.query.filter_by(
                slug=department_slug, is_active=True).first()
            if department:
                blog_query = blog_query.filter_by(department_id=department.id)

        # Filter by search query
        if search_query:
            blog_query = blog_query.filter(
                (Blog.title.ilike(f'%{search_query}%')) |
                (Blog.excerpt.ilike(f'%{search_query}%')) |
                (Blog.content.ilike(f'%{search_query}%'))
            )

        blogs = blog_query.order_by(Blog.created_at.desc()).all()

        return jsonify([{
            'id': blog.id,
            'title': blog.title,
            'excerpt': blog.excerpt,
            'content': blog.content,
            'image_path': blog.image_path,
            'department': blog.department.name if blog.department else 'General',
            'department_slug': blog.department.slug if blog.department else 'general',
            'created_at': blog.created_at.strftime('%B %d, %Y'),
            'slug': blog.slug
        } for blog in blogs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/guides')
def list_guides():
    # Fetch all active guides
    guides = Guide.query.filter_by(is_active=True).order_by(
        Guide.created_at.desc()).all()
    return render_template('guides.html', guides=guides)


@app.route('/guides/<slug>')
def guide_detail(slug):
    # Fetch a specific guide by its slug
    guide = Guide.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template('guide_detail.html', guide=guide)
# ----------------- BLOG HTML GENERATION FUNCTION -----------------


def remove_blog_html(slug):
    """Deletes the static HTML file for a blog post."""
    file_path = os.path.join(GENERATED_BLOG_FOLDER, f'{slug}.html')
    if os.path.exists(file_path):
        os.remove(file_path)


@app.route('/blog/<slug>/')
def blog_detail(slug):
    """
    Dynamic route: Fetches blog data from DB and renders the template on the fly.
    """
    # 1. Fetch from Database directly
    blog = Blog.query.filter_by(slug=slug, is_active=True).first_or_404()

    # 2. Logic for Related Blogs (Kept exactly as you had it)
    related_blogs = []
    has_department_blogs = False
    department_blog_count = 0

    if blog.department_id:
        # Get other blogs from the same department
        department_blogs = Blog.query.filter(
            Blog.department_id == blog.department_id,
            Blog.id != blog.id,
            Blog.is_active == True
        ).order_by(Blog.created_at.desc()).limit(6).all()

        department_blog_count = len(department_blogs)

        if department_blog_count > 0:
            related_blogs = department_blogs
            has_department_blogs = True

            if department_blog_count < 6:
                remaining_slots = 6 - department_blog_count
                # Supplement with general blogs
                general_blogs = Blog.query.filter(
                    Blog.id != blog.id,
                    Blog.is_active == True
                ).filter(
                    (Blog.department_id != blog.department_id) | (
                        Blog.department_id.is_(None))
                ).order_by(Blog.created_at.desc()).limit(remaining_slots).all()

                related_blogs.extend(general_blogs)
        else:
            # Fallback to general if department has no other blogs
            related_blogs = Blog.query.filter(
                Blog.id != blog.id,
                Blog.is_active == True
            ).order_by(Blog.created_at.desc()).limit(6).all()
    else:
        # General blogs if no department assigned
        related_blogs = Blog.query.filter(
            Blog.id != blog.id,
            Blog.is_active == True
        ).order_by(Blog.created_at.desc()).limit(6).all()

    # 3. Render the template directly (No file generation)
    return render_template('blog-detail.html',
                           blog=blog,
                           related_blogs=related_blogs,
                           has_department_blogs=has_department_blogs,
                           department_blog_count=department_blog_count)


def generate_blog_html(blog):
    """
    Generates the final static HTML file for a single blog post based on its slug.
    """
    if not blog or not blog.slug:
        return

    # Enhanced related blogs logic (same as above)
    related_blogs = []
    has_department_blogs = False
    department_blog_count = 0

    if blog.department_id:
        department_blogs = Blog.query.filter(
            Blog.department_id == blog.department_id,
            Blog.id != blog.id,
            Blog.is_active == True
        ).order_by(Blog.created_at.desc()).limit(6).all()

        department_blog_count = len(department_blogs)

        if department_blog_count > 0:
            related_blogs = department_blogs
            has_department_blogs = True

            if department_blog_count < 6:
                remaining_slots = 6 - department_blog_count

                # Get general blogs (blogs from other departments OR no department)
                general_blogs = Blog.query.filter(
                    Blog.id != blog.id,
                    Blog.is_active == True
                ).filter(
                    (Blog.department_id != blog.department_id) | (
                        Blog.department_id.is_(None))
                ).order_by(Blog.created_at.desc()).limit(remaining_slots).all()

                related_blogs.extend(general_blogs)
        else:
            related_blogs = Blog.query.filter(
                Blog.id != blog.id,
                Blog.is_active == True
            ).order_by(Blog.created_at.desc()).limit(6).all()
    else:
        related_blogs = Blog.query.filter(
            Blog.id != blog.id,
            Blog.is_active == True
        ).order_by(Blog.created_at.desc()).limit(6).all()

    # Use the application context for rendering templates outside of a request
    with app.app_context():
        # Render the 'blog-detail.html' template
        rendered_html = render_template(
            'blog-detail.html',
            blog=blog,
            related_blogs=related_blogs,
            has_department_blogs=has_department_blogs,
            department_blog_count=department_blog_count
        )

        # Define the file path: static/blog_pages/my-blog-slug.html
        file_path = os.path.join(GENERATED_BLOG_FOLDER, f'{blog.slug}.html')

        try:
            # Write the rendered content to the static file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
        except Exception as e:
            print(f"Error writing blog HTML: {e}")


@app.route('/admin/blogs', methods=['GET', 'POST'])
@login_required  # Assuming this decorator exists
@permission_required('blogs')  # Assuming this decorator exists
def admin_blogs():
    if request.method == 'POST':

        # ------------------------------------------------------------------
        # 1. DELETE Blog Logic (Handles deletion and redirects immediately)
        # ------------------------------------------------------------------
        if 'delete_id' in request.form:
            blog_id = request.form.get('delete_id')
            blog = Blog.query.get_or_404(blog_id)

            # Delete associated image if exists
            if blog.image_path:
                image_full_path = os.path.join(
                    app.static_folder, blog.image_path)
                if os.path.exists(image_full_path):
                    os.remove(image_full_path)

            db.session.delete(blog)
            db.session.commit()
            flash("Blog deleted successfully!", "success")
            return redirect(url_for('admin_blogs'))

        # ------------------------------------------------------------------
        # 2. RETRIEVE ALL FORM DATA (FIX FOR UnboundLocalError)
        #    Define all variables here, accessible by both Add and Update paths.
        # ------------------------------------------------------------------
        blog_id = request.form.get('blog_id')

        # Primary Content Fields
        title = request.form.get('title')
        slug = request.form.get('slug')
        excerpt = request.form.get('excerpt')
        content = request.form.get('content')
        department_id = request.form.get(
            'department_id') or None  # Use 'or None' for safety

        # NEW SEO FIELDS: Defined here to be globally accessible in this POST block
        meta_title = request.form.get('meta_title')
        meta_description = request.form.get('meta_description')
        canonical_url = request.form.get('canonical_url')

        # ------------------------------------------------------------------
        # 3. Handle Image Upload
        # ------------------------------------------------------------------
        image_path = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename != '':
                if allowed_file(image_file.filename):
                    filename = secure_filename(image_file.filename)
                    blogs_folder = os.path.join(
                        app.static_folder, 'img', 'blogs')
                    os.makedirs(blogs_folder, exist_ok=True)
                    full_path = os.path.join(blogs_folder, filename)
                    image_file.save(full_path)
                    image_path = f'img/blogs/{filename}'
                else:
                    flash(
                        'Invalid file type for blog image. Allowed: png, jpg, jpeg, gif, webp', 'error')
                    return redirect(url_for('admin_blogs'))

        # ------------------------------------------------------------------
        # 4. Add/Update Blog Logic
        # ------------------------------------------------------------------
        if blog_id:
            # Update existing blog
            blog = Blog.query.get_or_404(blog_id)

            # Check for slug conflict on update (if slug changed)
            if blog.slug != slug:
                existing = Blog.query.filter(
                    Blog.slug == slug, Blog.id != blog_id).first()
                if existing:
                    flash("A different blog already uses this slug.", "error")
                    return redirect(url_for('admin_blogs'))

            # Assigning fields (using the variables defined in Step 2)
            blog.title = title
            blog.slug = slug
            blog.excerpt = excerpt
            blog.content = content
            blog.department_id = department_id

            # SEO FIELDS: Now safely assigned
            blog.meta_title = meta_title
            blog.meta_description = meta_description
            blog.canonical_url = canonical_url

            # Update image if new one uploaded
            if image_path:
                # Delete old image if exists
                if blog.image_path:
                    old_image_path = os.path.join(
                        app.static_folder, blog.image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                blog.image_path = image_path

            db.session.commit()
            flash("Blog updated successfully!", "success")
        else:
            # Add new blog

            # Check for slug conflict on add
            existing = Blog.query.filter_by(slug=slug).first()
            if existing:
                flash("A blog with this slug already exists.", "error")
                return redirect(url_for('admin_blogs'))

            # Create new Blog object (using the variables defined in Step 2)
            blog = Blog(
                title=title,
                slug=slug,
                excerpt=excerpt,
                content=content,
                image_path=image_path,
                department_id=department_id,

                # SEO FIELDS: Safely assigned
                meta_title=meta_title,
                meta_description=meta_description,
                canonical_url=canonical_url
            )
            db.session.add(blog)
            db.session.commit()
            flash("Blog added successfully!", "success")

        # Final redirect after successful Add or Update
        return redirect(url_for('admin_blogs'))

    # ------------------------------------------------------------------
    # 5. GET Request Handling (This section displays the page)
    # ------------------------------------------------------------------
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    departments = Department.query.filter_by(is_active=True).all()

    # Fetch user access data for permissions
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content',
               'users', 'callback_requests', 'reviews', 'blogs']
    access = {module: False for module in modules}
    if user and user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    # Return the rendered template
    return render_template('admin/blogs.html', blogs=blogs, departments=departments, access=access, current_user=user)


@app.route('/admin/delete_blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)

    # Delete associated image if exists (Optional, keep if you want to clean images)
    if blog.image_path:
        image_full_path = os.path.join(app.static_folder, blog.image_path)
        if os.path.exists(image_full_path):
            os.remove(image_full_path)

    # Delete from DB
    db.session.delete(blog)
    db.session.commit()

    # REMOVE THE HTML FILE DELETION LOGIC HERE
    # (The lines checking GENERATED_BLOG_FOLDER and os.remove)

    flash('Blog deleted successfully!', 'success')
    return redirect(url_for('admin_blogs'))


@app.route('/api/blog/<int:blog_id>')
def get_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return {
        'id': blog.id,
        'title': blog.title,
        'slug': blog.slug,
        'excerpt': blog.excerpt or '',
        'content': blog.content or '',
        'department_id': blog.department_id,
        'image_path': blog.image_path or ''
    }


@app.route('/api/toggle_blog/<int:blog_id>', methods=['POST'])
def toggle_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog.is_active = not blog.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': blog.is_active})


@app.route('/test-blog-detail')
def test_blog_detail():
    try:
        # Get the first blog from database
        blog = Blog.query.filter_by(is_active=True).first()

        if not blog:
            return "No blogs found in database. Please create a blog first."

        # Test the template rendering
        return render_template('blog-detail.html', blog=blog, related_blogs=[])

    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/admin/upload', methods=['GET', 'POST'])
@login_required
@permission_required('bmw_report')  # Add this decorator
def admin_upload():
    # Get current user info properly
    admin_id = session.get("admin_id")
    user = User.query.get(admin_id)

    if not user:
        flash("Please log in first!", "warning")
        return redirect(url_for("admin_login"))

    if request.method == 'POST':
        file = request.files.get('pdf_file')
        if not file:
            flash('No file selected', 'danger')
            return redirect(url_for('admin_upload'))

        # Check if it's a PDF
        if not file.filename.lower().endswith('.pdf'):
            flash('Please upload a PDF file', 'danger')
            return redirect(url_for('admin_upload'))

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save file info to DB
        pdf_entry = BMWReportPDF(file_name=filename)
        db.session.add(pdf_entry)
        db.session.commit()

        flash('BMW Report uploaded successfully!', 'success')
        return redirect(url_for('admin_upload'))

    # Show all PDFs
    all_pdfs = BMWReportPDF.query.order_by(
        BMWReportPDF.uploaded_at.desc()).all()

    # Get user access for sidebar
    modules = ['banners', 'doctors', 'counters', 'testimonials', 'specialities',
               'departments', 'health_packages', 'sports_packages', 'department_content',
               'users', 'callback_requests', 'reviews', 'blogs', 'bmw_report', 'life_moments', 'guides']
    access = {module: False for module in modules}
    if user.access:
        for module in modules:
            access[module] = getattr(user.access, module, False)

    return render_template(
        'admin/admin_upload.html',
        all_pdfs=all_pdfs,
        access=access,
        current_user=user
    )


# ---------------- DELETE PDF ---------------- #
@app.route('/admin/delete/<int:pdf_id>', methods=['POST'])
def delete_pdf(pdf_id):
    pdf = BMWReportPDF.query.get_or_404(pdf_id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], pdf.file_name))
    except:
        pass
    db.session.delete(pdf)
    db.session.commit()
    flash('PDF deleted successfully!', 'success')
    return redirect(url_for('admin_upload'))


# ---------------- FRONTEND BMW REPORT PAGE ---------------- #
@app.route('/bmw_report')
def bmw_report():
    latest_pdf = BMWReportPDF.query.order_by(
        BMWReportPDF.uploaded_at.desc()).first()
    if latest_pdf:
        return redirect(url_for('serve_pdf', filename=latest_pdf.file_name))
    else:
        return "<h3 style='text-align:center;margin-top:50px;'>No BMW report uploaded yet.</h3>"


# ---------------- SERVE PDF FILE ---------------- #
@app.route('/uploads/<filename>')
def serve_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ------------------ ADMIN: Department Testimonials Management ------------------
@app.route('/admin/department_testimonials', methods=['GET', 'POST'])
@login_required
@permission_required('testimonials')
def admin_department_testimonials():
    if request.method == 'POST':
        # Delete testimonial
        if 'delete_id' in request.form:
            testimonial_id = request.form.get('delete_id')
            testimonial = DepartmentTestimonial.query.get_or_404(
                testimonial_id)
            db.session.delete(testimonial)
            db.session.commit()
            flash("Testimonial deleted successfully!", "success")
            return redirect(url_for('admin_department_overview'))

        # Add/Update testimonial
        testimonial_id = request.form.get('testimonial_id')

        if testimonial_id:
            # Update existing testimonial
            testimonial = DepartmentTestimonial.query.get_or_404(
                testimonial_id)
            testimonial.name = request.form.get('name')
            testimonial.comment = request.form.get('comment')
            testimonial.rating = int(request.form.get('rating', 5))
            testimonial.avatar_color = request.form.get('avatar_color')
            testimonial.department_id = request.form.get('department_id')
            testimonial.display_order = int(
                request.form.get('display_order', 0))

            db.session.commit()
            flash("Testimonial updated successfully!", "success")
        else:
            # Add new testimonial
            name = request.form.get('name')
            comment = request.form.get('comment')
            rating = int(request.form.get('rating', 5))
            avatar_color = request.form.get('avatar_color')
            department_id = request.form.get('department_id')
            display_order = int(request.form.get('display_order', 0))

            testimonial = DepartmentTestimonial(
                name=name,
                comment=comment,
                rating=rating,
                avatar_color=avatar_color,
                department_id=department_id,
                display_order=display_order
            )
            db.session.add(testimonial)
            db.session.commit()
            flash("Testimonial added successfully!", "success")

        return redirect(url_for('admin_department_overview'))

    # For GET requests, redirect to the main department overview page
    return redirect(url_for('admin_department_overview'))


# ✅ Toggle active/inactive testimonial
@app.route('/api/toggle_department_testimonial/<int:testimonial_id>', methods=['POST'])
@login_required
@permission_required('testimonials')
def toggle_department_testimonial(testimonial_id):
    testimonial = DepartmentTestimonial.query.get_or_404(testimonial_id)
    testimonial.is_active = not testimonial.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': testimonial.is_active})


# ------------------ ADMIN: FAQ Management ------------------
@app.route('/admin/faqs', methods=['GET', 'POST'])
@login_required
@permission_required('department_content')
def admin_faqs():
    if request.method == 'POST':
        # Delete FAQ
        if 'delete_id' in request.form:
            faq_id = request.form.get('delete_id')
            faq = FAQ.query.get_or_404(faq_id)
            db.session.delete(faq)
            db.session.commit()
            flash("FAQ deleted successfully!", "success")
            return redirect(url_for('admin_department_overview'))

        # Add/Update FAQ
        faq_id = request.form.get('faq_id')

        if faq_id:
            # Update existing FAQ
            faq = FAQ.query.get_or_404(faq_id)
            faq.question = request.form.get('question')
            faq.answer = request.form.get('answer')
            faq.department_id = request.form.get('department_id')
            faq.display_order = int(request.form.get('display_order', 0))

            db.session.commit()
            flash("FAQ updated successfully!", "success")
        else:
            # Add new FAQ
            question = request.form.get('question')
            answer = request.form.get('answer')
            department_id = request.form.get('department_id')
            display_order = int(request.form.get('display_order', 0))

            faq = FAQ(
                question=question,
                answer=answer,
                department_id=department_id,
                display_order=display_order
            )
            db.session.add(faq)
            db.session.commit()
            flash("FAQ added successfully!", "success")

        return redirect(url_for('admin_department_overview'))

    # For GET requests, redirect to the main department overview page
    return redirect(url_for('admin_department_overview'))


@app.route('/api/toggle_faq/<int:faq_id>', methods=['POST'])
def toggle_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    faq.is_active = not faq.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': faq.is_active})


# ------------------ DELETE ROUTES ------------------

# ✅ Delete Department Testimonial
@app.route('/admin/delete_testimonial/<int:testimonial_id>', methods=['POST'])
@login_required
@permission_required('testimonials')
def delete_department_testimonial(testimonial_id):
    testimonial = DepartmentTestimonial.query.get_or_404(testimonial_id)
    department_id = testimonial.department_id
    db.session.delete(testimonial)
    db.session.commit()

    # Regenerate department HTML
    department = Department.query.get(department_id)
    if department:
        generate_department_html(department)

    flash("Testimonial deleted successfully!", "success")
    return redirect(url_for('admin_department_overview'))


# ✅ Delete Department FAQ - FIXED PARAMETER NAME
@app.route('/admin/delete_faq/<int:faq_id>', methods=['POST'])
@login_required
@permission_required('department_content')
def delete_faq(faq_id):  # Changed from 'id' to 'faq_id'
    faq = FAQ.query.get_or_404(faq_id)
    department_id = faq.department_id
    db.session.delete(faq)
    db.session.commit()

    # Regenerate department HTML
    department = Department.query.get(department_id)
    if department:
        generate_department_html(department)

    flash("FAQ deleted successfully!", "success")
    return redirect(url_for('admin_department_overview'))


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

    app.run(host="0.0.0.0", port=2020, debug=True)
