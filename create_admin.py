# create_admin.py

from app import app, db
from models import User, UserAccess

def create_admin():
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print("Admin user already exists.")
            return
        
        admin = User(
            emp_id='admin001',
            name='Admin',
            email='admin@example.com',
            is_active=True
        )
        admin.set_password('adminpassword')
        db.session.add(admin)
        db.session.commit()

        access = UserAccess(
            user=admin,
            banners=True,
            doctors=True,
            counters=True,
            testimonials=True,
            specialities=True,
            departments=True,
            health_packages=True,
            sports_packages=True,
            department_content=True,
            users=True
        )
        db.session.add(access)
        db.session.commit()
        print("Admin user created successfully.")

if __name__ == '__main__':
    create_admin()
