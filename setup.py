from app import db, Admin, Teacher, Student
from app import app  # Import the Flask app instance

def setup_database():
    with app.app_context():  # Activate the application context
        db.create_all()

        # Add default admin
        admin = Admin(username="admin", password="admin123")
        db.session.add(admin)

        # Add default teacher
        teacher = Teacher(name="John Doe", subject="Math", password="teacher123")
        db.session.add(teacher)

        # Add default student
        student = Student(student_id="S001", name="Alice", class_name="10A")
        db.session.add(student)

        db.session.commit()
        print("Database initialized with default users.")

if __name__ == "__main__":
    setup_database()