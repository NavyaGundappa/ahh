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
    image_path = db.Column(db.String(300), nullable=False)
    alt_text = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.id}>'


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
    reviews = db.Column(db.Boolean, default=False)   # ✅ new field

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
