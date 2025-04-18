from flask_jwt_extended import get_jwt_identity
from app.controllers.api.admin import role_required
from flask import Blueprint, request, jsonify
from app.models.course_models import Course, CourseClass, CourseSchedule
from app.models.user import Instructor

instructor_bq = Blueprint('instructor', __name__)

@instructor_bq.route('/instructor/classes', methods=['GET'])
@role_required(['instructor'])
def get_instructor_classes():
    user_id = get_jwt_identity()
    instructor = Instructor.query.filter_by(user_id=user_id).first()
    if not instructor:
        return jsonify({'error': 'Instructor not found'}), 404

    classes = CourseClass.query.filter_by(instructor_id=instructor.id).all()
    result = [{
        'id': c.id,
        'class_code': c.class_code,
        'course_name': c.course.name,
        'semester': c.semester,
        'academic_year': c.academic_year
    } for c in classes]
    return jsonify(result)

@instructor_bq.route('/instructor/class/<int:id>', methods=['GET'])
@role_required(['instructor'])
def get_instructor_class_detail(id):
    course_class = CourseClass.query.get_or_404(id)
    return jsonify({
        'id': course_class.id,
        'class_code': course_class.class_code,
        'course_name': course_class.course.name,
        'semester': course_class.semester,
        'academic_year': course_class.academic_year,
        'major': course_class.major.name if course_class.major else None
    })
@instructor_bq.route('/instructor/schedules/<int:class_id>', methods=['GET'])
@role_required(['instructor'])
def get_instructor_schedule(class_id):
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