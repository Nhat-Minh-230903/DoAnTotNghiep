from app import db
from datetime import time

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    credit = db.Column(db.Integer)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'), nullable=True)

    faculty = db.relationship('Faculty', backref='courses')
    classes = db.relationship('CourseClass', backref='course', cascade="all, delete-orphan")


class CourseClass(db.Model):
    __tablename__ = 'course_classes'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=False)
    class_code = db.Column(db.String(20), unique=True, nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'), nullable=True)

    instructor = db.relationship('Instructor', backref='course_classes')
    major = db.relationship('Major', backref='course_classes')
    schedules = db.relationship('CourseSchedule', backref='course_class', cascade="all, delete-orphan")


class CourseSchedule(db.Model):
    __tablename__ = 'course_schedules'

    id = db.Column(db.Integer, primary_key=True)
    course_class_id = db.Column(db.Integer, db.ForeignKey('course_classes.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 1=Thứ 2 ... 7=Chủ nhật
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    building = db.Column(db.String(50))
    floor = db.Column(db.String(10))
    room = db.Column(db.String(20))
