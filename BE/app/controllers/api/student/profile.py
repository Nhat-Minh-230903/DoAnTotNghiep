from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import  Users, Student, Faculty, Major, Role, UserRole
from app import db

student_bp= Blueprint('student', __name__)

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_student_profile():
    user_id = get_jwt_identity()

    student = (
        db.session.query(Student, Users, Faculty, Major)
        .join(Users, Student.user_id == Users.id)
        .outerjoin(Faculty, Student.faculty_id == Faculty.id)
        .outerjoin(Major, Student.major_id == Major.id)
        .filter(Student.user_id == user_id)
        .first()
    )

    if not student:
        return jsonify({'error': 'Không tìm thấy thông tin sinh viên'}), 404

    student_info, user_info, faculty_info, major_info = student

    data = {
        'student_id': student_info.student_id,
        'name': user_info.name,
        'email': user_info.email,
        'phone': user_info.phone,
        'birth': user_info.birth,
        'gender': user_info.gender,
        'address': user_info.address,
        'faculty': faculty_info.name if faculty_info else None,
        'major': major_info.name if major_info else None,
        'enrollment_year': student_info.enrollment_year
    }

    return jsonify({'data': data}), 200



@student_bp.route('/get_user_roles/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_roles(user_id):
    current_user_id = get_jwt_identity()
    current_user_roles = (
        db.session.query(Role.name)
        .join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == current_user_id)
        .all()
    )
    current_user_roles = [r[0] for r in current_user_roles]

    if current_user_id != user_id  not in current_user_roles:
        return jsonify({'error': 'Bạn không có quyền xem vai trò của người dùng này'}), 403

    user = Users.query.get(user_id)
    if not user or user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc đã bị xoá'}), 404

    roles = (
        db.session.query(Role.id, Role.name)
        .join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == user_id)
        .all()
    )

    role_list = [{'id': r.id, 'name': r.name} for r in roles]

    return jsonify({
        'user_id': user.id,
        'user_name': user.name,
        'roles': role_list
    }), 200