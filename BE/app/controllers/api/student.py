from flask_jwt_extended import get_jwt_identity
from app.controllers.api.admin import role_required
from flask import Blueprint, request, jsonify
from app.models.course_models import Course, CourseClass, CourseSchedule
from app.models.user import Student

student_bq= Blueprint('student', __name__)

@student_bq.route('/student/classes', methods=['GET'])
@role_required(['student'])
def get_student_classes():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    course_classes = CourseClass.query.filter_by(major_id=student.major_id).all()
    result = [{
        'id': cc.id,
        'class_code': cc.class_code,
        'course_name': cc.course.name,
        'semester': cc.semester,
        'academic_year': cc.academic_year
    } for cc in course_classes]
    return jsonify(result)
@student_bq.route('/student/class/<int:id>', methods=['GET'])
@role_required(['student'])
def get_student_class_detail(id):
    course_class = CourseClass.query.get_or_404(id)
    return jsonify({
        'id': course_class.id,
        'class_code': course_class.class_code,
        'course_name': course_class.course.name,
        'semester': course_class.semester,
        'academic_year': course_class.academic_year,
        'instructor': course_class.instructor.full_name
    })
@student_bq.route('/student/schedules/<int:class_id>', methods=['GET'])
@role_required(['student'])
def get_student_class_schedule(class_id):
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
