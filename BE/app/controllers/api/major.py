from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Major, Faculty
from app.utils.course_helper import generate_prefix_from_name
from app.controllers.api.admin import role_required

major_bp = Blueprint('major_bp', __name__)

# Kiểm tra trùng lặp mã chuyên ngành
def is_duplicate_major_name(name, faculty_id, exclude_id=None):
    query = Major.query.filter_by(name=name, faculty_id=faculty_id)
    if exclude_id:
        query = query.filter(Major.id != exclude_id)
    return db.session.query(query.exists()).scalar()

@major_bp.route('', methods=['GET'])
@role_required(['Admin'])
def get_all_major():
    majors = Major.query.all()
    data = [{
        'id': m.id,
        'name': m.name,
        'prefix': m.prefix,
        'faculty_id': m.faculty_id
    } for m in majors]
    return jsonify(data)

@major_bp.route('', methods=['POST'])
@role_required(['Admin'])
def add_major():
    data = request.get_json()
    name = data.get('name')
    faculty_id = data.get('faculty_id')

    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    # Kiểm tra trùng lặp trước khi thêm
    if is_duplicate_major_name(name, faculty_id):
        return jsonify({"error": "Major name already exists for this faculty"}), 400
    
    prefix = generate_prefix_from_name(name)
    new_major = Major(name=name, faculty_id=faculty_id, prefix=prefix)
    
    db.session.add(new_major)
    db.session.commit()
    
    return jsonify({"message": "Major added successfully"}), 201

@major_bp.route('/<int:id>', methods=['PUT'])
@role_required(['Admin'])
def update_major(id):
    data = request.get_json()
    name = data.get('name')
    faculty_id = data.get('faculty_id')

    major = Major.query.get(id)
    if not major:
        return jsonify({"error": "Major not found"}), 404
    
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404
    
    # Kiểm tra trùng lặp trước khi cập nhật
    if is_duplicate_major_name(name, faculty_id, exclude_id=id):
        return jsonify({"error": "Major name already exists for this faculty"}), 400
    
    major.name = name
    major.faculty_id = faculty_id
    major.prefix = generate_prefix_from_name(name)
    
    db.session.commit()
    
    return jsonify({"message": "Major updated successfully"}), 200

@major_bp.route('/major/<int:id>', methods=['DELETE'])
@role_required(['Admin'])
def delete_major(id):
    major = Major.query.get(id)
    if not major:
        return jsonify({"error": "Major not found"}), 404
    
    db.session.delete(major)
    db.session.commit()
    
    return jsonify({"message": "Major deleted successfully"}), 200
