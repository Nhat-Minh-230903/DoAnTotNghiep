from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Users, Students, Enrollments, CourseClasses, Courses, CourseSchedules

student_bp= Blueprint('student', __name__)
@student_bp.route('/my-schedule', methods=['GET'])
@jwt_required()
def get_student_schedule():
    user_id = get_jwt_identity()

    student = Students.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'Không tìm thấy sinh viên'}), 404

    results = (
        db.session.query(CourseSchedules, CourseClasses, Courses)
        .join(CourseClasses, CourseSchedules.course_class_id == CourseClasses.id)
        .join(Enrollments, Enrollments.course_class_id == CourseClasses.id)
        .join(Courses, CourseClasses.course_id == Courses.id)
        .filter(Enrollments.student_id == student.id)
        .all()
    )

    data = []
    for schedule, course_class, course in results:
        data.append({
            'course_name': course.name,
            'class_code': course_class.class_code,
            'day_of_week': schedule.day_of_week,  # 1 = Thứ 2, ..., 7 = Chủ nhật
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'building': schedule.building,
            'floor': schedule.floor,
            'room': schedule.room
        })

    return jsonify({'data': data}), 200
