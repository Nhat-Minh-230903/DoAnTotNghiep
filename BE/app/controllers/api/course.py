from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from models.course_models import Course, CourseClass, CourseSchedule
from models import Instructor, Student  # nếu cần
from sqlalchemy.exc import IntegrityError
from admin import role_required

course_bp = Blueprint('course', __name__)
@course_bp.route('/', methods=['GET'])
@role_required(['admin'])
def get_all_courses():
    courses = Course.query.all()
    data = [{
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'credit': c.credit,
        'faculty_id': c.faculty_id
    } for c in courses]
    return jsonify(data)


@course_bp.route('/', methods=['POST'])
@role_required(['admin'])
def create_course():
    data = request.get_json()
    try:
        course = Course(
            code=data['code'],
            name=data['name'],
            credit=data.get('credit', 0),
            faculty_id=data.get('faculty_id')
        )
        db.session.add(course)
        db.session.commit()
        return jsonify({'message': 'Course created', 'id': course.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Course code must be unique'}), 400


@course_bp.route('/<int:id>', methods=['PUT'])
@role_required(['admin'])
def update_course(id):
    course = Course.query.get_or_404(id)
    data = request.get_json()
    course.code = data.get('code', course.code)
    course.name = data.get('name', course.name)
    course.credit = data.get('credit', course.credit)
    course.faculty_id = data.get('faculty_id', course.faculty_id)
    db.session.commit()
    return jsonify({'message': 'Course updated'})


@course_bp.route('/<int:id>', methods=['DELETE'])
@role_required(['admin'])
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted'})



@course_bp.route('/classes', methods=['POST'])
@role_required(['admin'])
def create_course_class():
    data = request.get_json()
    course_class = CourseClass(
        course_id=data['course_id'],
        instructor_id=data['instructor_id'],
        class_code=data['class_code'],
        semester=data['semester'],
        academic_year=data['academic_year'],
        major_id=data.get('major_id')
    )
    db.session.add(course_class)
    db.session.commit()
    return jsonify({'message': 'Course class created', 'id': course_class.id})

@course_bp.route('/classes/<int:id>', methods=['PUT'])
@role_required(['admin'])
def update_course_class(id):
    data = request.get_json()
    course_class = CourseClass.query.get_or_404(id)

    course_class.course_id = data.get('course_id', course_class.course_id)
    course_class.instructor_id = data.get('instructor_id', course_class.instructor_id)
    course_class.class_code = data.get('class_code', course_class.class_code)
    course_class.semester = data.get('semester', course_class.semester)
    course_class.academic_year = data.get('academic_year', course_class.academic_year)
    course_class.major_id = data.get('major_id', course_class.major_id)

    db.session.commit()
    return jsonify({'message': 'Course class updated'})


@course_bp.route('/classes/<int:instructor_id>', methods=['GET'])
@role_required(['admin'])
def get_classes_by_instructor(instructor_id):
    classes = CourseClass.query.filter_by(instructor_id=instructor_id).all()
    result = [{
        'id': c.id,
        'class_code': c.class_code,
        'course_name': c.course.name,
        'semester': c.semester,
        'academic_year': c.academic_year
    } for c in classes]
    return jsonify(result)


@course_bp.route('/classes/<int:id>', methods=['DELETE'])
@role_required(['admin'])
def delete_course_class(id):
    course_class = CourseClass.query.get_or_404(id)
    db.session.delete(course_class)
    db.session.commit()
    return jsonify({'message': 'Course class deleted'})




@course_bp.route('/schedules', methods=['POST'])
@role_required(['admin'])
def create_schedule():
    data = request.get_json()
    schedule = CourseSchedule(
        course_class_id=data['course_class_id'],
        day_of_week=data['day_of_week'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        building=data.get('building'),
        floor=data.get('floor'),
        room=data.get('room')
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify({'message': 'Schedule created', 'id': schedule.id})

@course_bp.route('/schedules/<int:id>', methods=['PUT'])
@role_required(['admin'])
def update_schedule(id):
    data = request.get_json()
    schedule = CourseSchedule.query.get_or_404(id)

    schedule.course_class_id = data.get('course_class_id', schedule.course_class_id)
    schedule.day_of_week = data.get('day_of_week', schedule.day_of_week)
    schedule.start_time = data.get('start_time', schedule.start_time)
    schedule.end_time = data.get('end_time', schedule.end_time)
    schedule.building = data.get('building', schedule.building)
    schedule.floor = data.get('floor', schedule.floor)
    schedule.room = data.get('room', schedule.room)

    db.session.commit()
    return jsonify({'message': 'Schedule updated'})

@course_bp.route('/schedules/<int:class_id>', methods=['GET'])
@role_required(['admin'])
def get_schedules_by_class(class_id):
    schedules = CourseSchedule.query.filter_by(course_class_id=class_id).all()
    result = [{
        'day_of_week': s.day_of_week,
        'start_time': s.start_time.strftime('%H:%M'),
        'end_time': s.end_time.strftime('%H:%M'),
        'building': s.building,
        'floor': s.floor,
        'room': s.room
    } for s in schedules]
    return jsonify(result)


@course_bp.route('/schedules/<int:id>', methods=['DELETE'])
@role_required(['admin'])
def delete_schedule(id):
    schedule = CourseSchedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'message': 'Schedule deleted'})

