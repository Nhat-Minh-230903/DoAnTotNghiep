# # Xem các lớp giảng viên đang dạy
# from flask import Blueprint, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from models import db, Users, Students, Faculties, Majors, Courses, CourseClasses, Enrollments, CourseSchedules,Instructors, Faculty
# from app.controllers.api.admin.admin import role_required

# instructor_bp = Blueprint('instructor', __name__)
# @instructor_bp.route('/my-classes', methods=['GET'])
# @jwt_required()
# @role_required(['Instructor'])
# def get_instructor_classes():
#     user_id = get_jwt_identity()
#     instructor = Instructors.query.filter_by(user_id=user_id).first()

#     if not instructor:
#         return jsonify({'error': 'Không tìm thấy giảng viên'}), 404

#     results = (
#         db.session.query(CourseClasses, Courses)
#         .join(Courses, CourseClasses.course_id == Courses.id)
#         .filter(CourseClasses.instructor_id == instructor.id)
#         .all()
#     )

#     data = []
#     for cls, course in results:
#         data.append({
#             'class_code': cls.class_code,
#             'course_name': course.name,
#             'course_code': course.code,
#             'semester': cls.semester,
#             'academic_year': cls.academic_year
#         })

#     return jsonify({'data': data})

# # Xem lịch dạy của giảng viên   
# @instructor_bp.route('/my-schedule', methods=['GET'])
# @jwt_required()
# @role_required(['Instructor'])
# def get_instructor_schedule():
#     user_id = get_jwt_identity()
#     instructor = Instructors.query.filter_by(user_id=user_id).first()

#     if not instructor:
#         return jsonify({'error': 'Không tìm thấy giảng viên'}), 404

#     results = (
#         db.session.query(CourseSchedules, CourseClasses, Courses)
#         .join(CourseClasses, CourseSchedules.course_class_id == CourseClasses.id)
#         .join(Courses, CourseClasses.course_id == Courses.id)
#         .filter(CourseClasses.instructor_id == instructor.id)
#         .all()
#     )

#     data = []
#     for schedule, cls, course in results:
#         data.append({
#             'course_name': course.name,
#             'class_code': cls.class_code,
#             'day_of_week': schedule.day_of_week,
#             'start_time': schedule.start_time.strftime('%H:%M'),
#             'end_time': schedule.end_time.strftime('%H:%M'),
#             'building': schedule.building,
#             'floor': schedule.floor,
#             'room': schedule.room
#         })

#     return jsonify({'data': data})