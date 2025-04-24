from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Faculty
from app.utils.course_helper import generate_prefix_from_name
from app.controllers.api.admin import role_required

faculty_bp = Blueprint('faculty_bp', __name__)

# Kiểm tra trùng lặp mã ngành
def is_duplicate_faculty_name(name, exclude_id=None):
    query = Faculty.query.filter_by(name=name)
    if exclude_id:
        query = query.filter(Faculty.id != exclude_id)
    return db.session.query(query.exists()).scalar()

@faculty_bp.route('', methods=['GET'])
@role_required(['Admin'])
def get_all_faculty():
    faculty=Faculty.query.all()
    data = [{
        'id':c.id,
        'name':c.name,
        'prefix':c.prefix
    }for c in faculty]
    return jsonify(data)



@faculty_bp.route('', methods=['POST'])
@role_required(['Admin'])
def add_faculty():
    data = request.get_json()
    name = data.get('name')
    if is_duplicate_faculty_name(name):
        return jsonify({"error": "Faculty name already exists"}), 400
    
    prefix = generate_prefix_from_name(name)
    new_faculty = Faculty(name=name, prefix=prefix)
    
    db.session.add(new_faculty)
    db.session.commit()
    
    return jsonify({"message": "Faculty added successfully"}), 201

@faculty_bp.route('/faculty/<int:id>', methods=['PUT'])
@role_required(['Admin'])
def update_faculty(id):
    data = request.get_json()
    name = data.get('name')
    
    faculty = Faculty.query.get(id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    # Kiểm tra trùng lặp trước khi cập nhật
    if is_duplicate_faculty_name(name, exclude_id=id):
        return jsonify({"error": "Faculty name already exists"}), 400
    
    faculty.name = name
    faculty.prefix = generate_prefix_from_name(name)
    
    db.session.commit()
    
    return jsonify({"message": "Faculty updated successfully"}), 200

@faculty_bp.route('/faculty/<int:id>', methods=['DELETE'])
@role_required(['Admin'])
def delete_faculty(id):
    faculty = Faculty.query.get(id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404
    
    db.session.delete(faculty)
    db.session.commit()
    
    return jsonify({"message": "Faculty deleted successfully"}), 200
