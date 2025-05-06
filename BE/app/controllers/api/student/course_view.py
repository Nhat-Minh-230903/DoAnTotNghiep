from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Users, Students, Enrollments, CourseClasses, Courses, Instructors, Users as InstructorUsers

student_bp= Blueprint('student', __name__)
@student_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_student_courses():
    user_id = get_jwt_identity()

    student = Students.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'Không tìm thấy sinh viên'}), 404

    results = (
        db.session.query(CourseClasses, Courses, Instructors, InstructorUsers)
        .join(Enrollments, Enrollments.course_class_id == CourseClasses.id)
        .join(Courses, CourseClasses.course_id == Courses.id)
        .join(Instructors, CourseClasses.instructor_id == Instructors.id)
        .join(InstructorUsers, Instructors.user_id == InstructorUsers.id)
        .filter(Enrollments.student_id == student.id)
        .all()
    )

    data = []
    for cls, course, instructor, instructor_user in results:
        data.append({
            'course_code': course.code,
            'course_name': course.name,
            'credit': course.credit,
            'class_code': cls.class_code,
            'semester': cls.semester,
            'academic_year': cls.academic_year,
            'instructor_name': instructor_user.name,
        })

    return jsonify({'data': data}), 200
