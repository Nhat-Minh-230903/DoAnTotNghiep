from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import Users
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import Users,Student, Instructor, UserRole, Role,Faculty,Major

user_bp = Blueprint('user', __name__)

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    user = Users.query.get(user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404

    # Lấy vai trò người dùng
    user_role = (
        db.session.query(Role.name)
        .join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == user.id)
        .first()
    )
    role = user_role[0] if user_role else "Không có"

    # Thông tin cơ bản người dùng
    user_data = {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'phone': user.phone,
        'birth': user.birth,
        'gender': user.gender,
        'address': user.address,
        'status': user.status,
        'first_login': user.first_login,
        'role': role
    }

    # Nếu là sinh viên
    student = Student.query.filter_by(user_id=user.id).first()
    if student:
        faculty = Faculty.query.get(student.faculty_id)
        major = Major.query.get(student.major_id)
        user_data.update({
            'student_id': student.student_id,
            'faculty': faculty.name if faculty else None,
            'major': major.name if major else None,
            'enrollment_year': student.enrollment_year
        })

    # Nếu là giảng viên
    instructor = Instructor.query.filter_by(user_id=user.id).first()
    if instructor:
        faculty = Faculty.query.get(instructor.faculty_id)
        user_data.update({
            'employee_id': instructor.employee_id,
            'faculty': faculty.name if faculty else None,
            'position': instructor.position,
            'degree': instructor.degree,
            'joined_year': instructor.joined_year
        })

    return jsonify(user_data), 200
