from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Admin, Teacher, Student, Exam, Marks
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'

db.init_app(app)


@app.route('/')
def home():
    return render_template('home.html')

#contact
@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/main')
def index():
    return render_template('login.html')


# Admin Login
@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    admin = Admin.query.filter_by(username=username, password=password).first()
    if admin:
        session['user'] = 'admin'
        return redirect(url_for('admin_dashboard'))
    return "Invalid Details"

#admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('user') == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for('index'))

#add teacher
@app.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        password = request.form['password']
        new_teacher = Teacher(name=name, subject=subject, password=password)
        try:
            db.session.add(new_teacher)
            db.session.commit()
        except IntegrityError:
            return "Teacher already exists."
        return redirect(url_for('view_teachers'))
    return render_template('add_teacher.html')

#view teacher
@app.route('/view_teachers')
def view_teachers():
    teachers = Teacher.query.all()
    return render_template('view_teachers.html', teachers=teachers)

#remove teacher
@app.route('/remove_teacher/<int:teacher_id>',methods=['POST'])
def remove_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        db.session.delete(teacher)
        db.session.commit()
        return redirect(url_for('view_teachers'))
    return "Teacher not found"

#add student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        class_name = request.form['class']
        new_student = Student(student_id=student_id, name=name, class_name=class_name)
        try:
            db.session.add(new_student)
            db.session.commit()
        except IntegrityError:
            return "Student already exists."
        return redirect(url_for('view_students'))
    return render_template('add_student.html')

#view student
@app.route('/view_students')
def view_students():
    students = Student.query.all()
    return render_template('view_students.html', students=students)

#remove student
@app.route('/remove_student/<int:student_id>',methods=['POST'])
def remove_student(student_id):
    student=Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return redirect(url_for('view_students'))
    return "Student not found"

#add exam
@app.route('/add_exam', methods=['GET', 'POST'])
def add_exam():
    if request.method == 'POST':
        exam_type = request.form['type']
        subject = request.form['subject']
        new_exam = Exam(exam_type=exam_type, subject=subject)
        db.session.add(new_exam)
        db.session.commit()
        return redirect(url_for('view_exams'))
    return render_template('add_exam.html')

#view exams
@app.route('/view_exams')
def view_exams():
    exams = Exam.query.all()
    return render_template('view_exams.html', exams=exams)

#remove exam
@app.route('/remove_exam/<int:exam_id>',methods=['POST'])
def remove_exam(exam_id):
    exam = Exam.query.get(exam_id)
    if exam:
        db.session.delete(exam)
        db.session.commit()
        return redirect(url_for('view_exams'))
    return "Exam not found"


#teacher login
@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        
        # Query the Teacher table
        teacher = Teacher.query.filter_by(name=name, password=password).first()
        
        if teacher:
            session['user'] = 'teacher'
            session['teacher_id'] = teacher.id
            return redirect(url_for('teacher_dashboard', page=1))
        else:
            return "Invalid Teacher credentials. Please try again."
    return render_template('teacher_login.html')





@app.route('/teacher_dashboard/<int:page>', methods=['GET', 'POST'])
def teacher_dashboard(page=1):
    per_page = 30  # Number of students per page
    students = Student.query.order_by(Student.class_name).paginate(page=page, per_page=per_page)
    exams = Exam.query.all()  # Fetch all exams

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        exam_id = request.form.get('exam_id')
        marks = request.form.get('marks')

        # Validate the input
        if not marks or not marks.replace('.', '', 1).isdigit():
            return "Invalid marks input. Please enter a valid number.", 400

        # Convert marks to float
        marks = float(marks)

        # Check if marks entry already exists
        existing_marks = Marks.query.filter_by(student_id=student_id, exam_id=exam_id).first()
        if existing_marks:
            # Update marks
            existing_marks.marks = marks
        else:
            # Add new marks entry
            new_marks = Marks(student_id=student_id, exam_id=exam_id, marks=marks)
            db.session.add(new_marks)

        db.session.commit()

    return render_template('teacher_dashboard.html', students=students, exams=exams, page=page)
#view students marks
@app.route('/view_students_marks/<int:page>', methods=['GET'])
def view_students_marks(page=1):
    per_page = 30
    students = Student.query.order_by(Student.class_name).paginate(page=page, per_page=per_page)
    exams = Exam.query.all()

    # Construct marks_dict efficiently
    marks_dict = {}
    for mark in Marks.query.all():
        student_id = int(mark.student_id)
        exam_id = int(mark.exam_id)

        if student_id not in marks_dict:
            marks_dict[student_id] = {}
        marks_dict[student_id][exam_id] = mark.marks
        
    return render_template(
        'view_marks.html',
        students=students,
        exams=exams,
        marks_dict=marks_dict,
        page=page
    )

# Student Login
@app.route('/student_login', methods=['POST'])
def student_login():
    student_id = request.form['student_id']
    name = request.form['name']
    student = Student.query.filter_by(student_id=student_id, name=name).first()
    if student:
        session['user'] = 'student'
        session['student_id'] = student.id
        return redirect(url_for('student_dashboard'))
    return "Invalid credentials"

#student dashboard
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('user') == 'student':
        student_id = session['student_id']
        marks = Marks.query.filter_by(student_id=student_id).all()
        return render_template('view_student_marks.html', marks=marks)
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)





