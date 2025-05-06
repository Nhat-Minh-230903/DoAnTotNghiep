
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import Faculty,Users,Instructor

instructor_bp = Blueprint('instructor_bp', __name__)

@instructor_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_instructor_profile():
    user_id = get_jwt_identity()

    user = Users.query.get(user_id)
    instructor = Instructors.query.filter_by(user_id=user_id).first()

    if not user or not instructor:
        return jsonify({'error': 'Không tìm thấy thông tin'}), 404

    faculty = Faculty.query.get(instructor.faculty_id)

    return jsonify({
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'birth': user.birth,
        'gender': user.gender,
        'address': user.address,
        'position': instructor.position,
        'degree': instructor.degree,
        'joined_year': instructor.joined_year,
        'faculty': faculty.name if faculty else None
    }), 200
