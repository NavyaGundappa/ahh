from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    alt_text = db.Column(db.String(200))
    button_text = db.Column(db.String(100), nullable=True)
    button_link = db.Column(db.String(300), nullable=True)
    alt_text = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Banner {self.title}>'


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(200), nullable=False)
    designation = db.Column(db.String(200), nullable=True)
    experience = db.Column(db.String(100), nullable=True)
    qualification = db.Column(db.String(200), nullable=True)
    languages = db.Column(db.String(200), nullable=True)
    overview = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0)
    fellowship_membership = db.Column(db.Text, nullable=True)
    fellowship_links = db.Column(db.Text, nullable=True)
    fellowship_file_path = db.Column(db.String(300), nullable=True)

    field_of_expertise = db.Column(db.Text, nullable=True)

    talks_and_publications = db.Column(db.Text, nullable=True)
    talks_links = db.Column(db.Text, nullable=True)
    talks_file_path = db.Column(db.String(300), nullable=True)

    bio = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(300), nullable=True)
    appointment_link = db.Column(db.String(300), nullable=True)

    department_slug = db.Column(db.String(150), nullable=True)

    # ✅ Store timings as JSON string
    timings = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(150), unique=True, nullable=False)

    def __repr__(self):
        return f"<Doctor {self.name}>"


class CallbackRequest(db.Model):
    __tablename__ = 'callback_requests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    package_name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CallbackRequest {self.name} - {self.phone}>"


class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    suffix = db.Column(db.String(10), default='+')
    icon_path = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Counter {self.label}: {self.count}>'


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # --- ADD THIS LINE ---
    youtube_link = db.Column(db.String(300), nullable=True)
    # ---------------------
    doctor_id = db.Column(db.Integer, db.ForeignKey(
        'doctors.id'), nullable=False)
    doctor = db.relationship('Doctor', foreign_keys=[
                             doctor_id], backref=db.backref('primary_testimonials', lazy=True))
    doctor2_id = db.Column(
        db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    doctor2 = db.relationship('Doctor', foreign_keys=[
                              doctor2_id], backref=db.backref('secondary_testimonials', lazy=True))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.patient_name}>'


class LifeMoment(db.Model):
    __tablename__ = 'life_moments'

    id = db.Column(db.Integer, primary_key=True)
    # Categories: 'patient_stories', 'doctors_speak', 'general', 'health_days', 'events', 'written_testimonial'
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # For Videos (YouTube)
    video_link = db.Column(db.String(300), nullable=True)
    # Primary Doctor Link
    doctor1_id = db.Column(
        db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    doctor1 = db.relationship('Doctor', foreign_keys=[
                              doctor1_id], backref='life_moments_as_doctor1')

    # Secondary Doctor Link (NEW)
    doctor2_id = db.Column(
        db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    doctor2 = db.relationship('Doctor', foreign_keys=[
                              doctor2_id], backref='life_moments_as_doctor2')

    # For Images (Events/Health Days/Thumbnails)
    image_path = db.Column(db.String(300), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LifeMoment {self.title} ({self.category})>'


class Speciality(db.Model):
    __tablename__ = 'specialities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail_path = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Speciality {self.name}>'


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon_path = db.Column(db.String(300), nullable=True)
    # ✅ new column for banner image
    banner_path = db.Column(db.String(300), nullable=True)
    banner_alt_text = db.Column(db.String(300), nullable=True)
    # ✅ NEW FIELDS for specialists section
    specialists_heading = db.Column(db.String(500), nullable=True)
    specialists_content = db.Column(db.Text, nullable=True)
    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.Text, nullable=True)
    canonical_url = db.Column(db.String(500), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Department {self.name}>"


class HealthPackage(db.Model):
    __tablename__ = 'health_packages'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    # 'male', 'female', or None
    gender = db.Column(db.String(20), nullable=True)
    original_price = db.Column(db.Float, nullable=False)
    offer_price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=True)
    is_best_value = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    # JSON string or comma-separated
    tests = db.Column(db.Text, nullable=False)
    important_info = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<HealthPackage {self.title}>'


class SportsPackage(db.Model):
    __tablename__ = 'sports_packages'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    # e.g., "Cricket", "Football", etc.
    sport_type = db.Column(db.String(100), nullable=True)
    original_price = db.Column(db.Float, nullable=False)
    offer_price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=True)
    is_best_value = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    # JSON string or comma-separated
    tests = db.Column(db.Text, nullable=False)
    important_info = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SportsPackage {self.title}>'


# ------------------ Department Overview ------------------
class DepartmentOverview(db.Model):
    __tablename__ = 'department_overviews'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # overview text content
    quote = db.Column(db.Text, nullable=True)     # blockquote text
    quote_author = db.Column(db.String(200), nullable=True)

    department_id = db.Column(db.Integer, db.ForeignKey(
        'departments.id'), nullable=False)
    department = db.relationship('Department', backref=db.backref(
        'overview', lazy=True, uselist=False))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Overview {self.department.name}>"

# ------------------ Department Services ------------------


class DepartmentService(db.Model):
    __tablename__ = 'department_services'

    id = db.Column(db.Integer, primary_key=True)
    # e.g., General, Regional
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)     # text / paragraph
    icon_path = db.Column(db.String(300), nullable=True)  # path to svg/png
    # store bullet points as comma-separated text
    list_items = db.Column(db.Text, nullable=True)

    # ✅ RENAMED FIELD for services overview
    services_overview = db.Column(db.Text, nullable=True)

    department_id = db.Column(db.Integer, db.ForeignKey(
        'departments.id'), nullable=False)
    department = db.relationship(
        'Department', backref=db.backref('services', lazy=True))

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_list_items(self):
        if self.list_items:
            return self.list_items.split(",")
        return []

    def __repr__(self):
        return f"<Service {self.title}>"


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    access = db.relationship(
        'UserAccess', backref='user', lazy=True, uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserAccess(db.Model):
    __tablename__ = 'user_access'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    banners = db.Column(db.Boolean, default=False)
    doctors = db.Column(db.Boolean, default=False)
    counters = db.Column(db.Boolean, default=False)
    testimonials = db.Column(db.Boolean, default=False)
    specialities = db.Column(db.Boolean, default=False)
    departments = db.Column(db.Boolean, default=False)
    health_packages = db.Column(db.Boolean, default=False)
    sports_packages = db.Column(db.Boolean, default=False)
    department_content = db.Column(db.Boolean, default=False)
    users = db.Column(db.Boolean, default=False)
    callback_requests = db.Column(db.Boolean, default=False)
    reviews = db.Column(db.Boolean, default=False)
    blogs = db.Column(db.Boolean, default=False)
    bmw_report = db.Column(db.Boolean, default=False)
    life_moments = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ReviewMessage(db.Model):
    __tablename__ = "review_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ReviewMessage {self.name}>"


class Guide(db.Model):
    __tablename__ = 'guides'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    header_image_path = db.Column(db.String(255))
    content_image_path = db.Column(db.String(255))
    # This will store the HTML from your admin WYSIWYG editor
    content = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(300), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey(
        'departments.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.Text, nullable=True)
    canonical_url = db.Column(db.String(255), nullable=True)

    # Relationship
    department = db.relationship('Department', backref='blogs')

    def __repr__(self):
        return f"<Blog {self.title}>"


class BMWReportPDF(db.Model):
    __tablename__ = 'bmw_report_pdfs'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class DepartmentTestimonial(db.Model):
    __tablename__ = 'department_testimonials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    avatar_color = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    department_id = db.Column(db.Integer, db.ForeignKey(
        'departments.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = db.relationship('Department', backref=db.backref(
        'department_testimonials', lazy=True))


class FAQ(db.Model):
    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    department_id = db.Column(db.Integer, db.ForeignKey(
        'departments.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = db.relationship(
        'Department', backref=db.backref('faqs', lazy=True))
