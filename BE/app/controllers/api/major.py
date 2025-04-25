from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Major, Faculty
from app.utils.course_helper import generate_prefix_from_name
from app.controllers.api.admin import role_required
import os
from werkzeug.utils import secure_filename
import pandas as pd
major_bp = Blueprint('major_bp', __name__)

# Kiểm tra trùng lặp tên chuyên ngành
def is_duplicate_major_name(name, exclude_id=None):
    query = Major.query.filter_by(name=name)
    if exclude_id:
        query = query.filter(Major.id != exclude_id)
    return db.session.query(query.exists()).scalar()

@major_bp.route('', methods=['GET'])
@role_required(['Admin'])
def get_all_majors():
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

    if not name or not faculty_id:
        return jsonify({"error": "Missing required fields"}), 400

    if is_duplicate_major_name(name):
        return jsonify({"error": "Major name already exists"}), 400

    prefix = generate_prefix_from_name(name)
    new_major = Major(name=name, prefix=prefix, faculty_id=faculty_id)

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

    if name == major.name:
        return jsonify({"error": "Please change the major name"}), 400

    if is_duplicate_major_name(name, exclude_id=id):
        return jsonify({"error": "Major name already exists"}), 400

    major.name = name
    major.prefix = generate_prefix_from_name(name)
    major.faculty_id = faculty_id

    db.session.commit()
    return jsonify({"message": "Major updated successfully"}), 200


@major_bp.route('/<int:id>', methods=['DELETE'])
@role_required(['Admin'])
def delete_major(id):
    major = Major.query.get(id)
    if not major:
        return jsonify({"error": "Major not found"}), 404

    db.session.delete(major)
    db.session.commit()
    return jsonify({"message": "Major deleted successfully"}), 200


@major_bp.route('/add_majors/<int:faculty_id>', methods=['POST'])
@role_required(['Admin'])  # Kiểm tra quyền Admin
def add_majors(faculty_id):
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({"error": f"Faculty with ID {faculty_id} not found"}), 404

    major_names = request.json.get('major_names', [])

    added = 0
    skipped = 0

    for name in major_names:
        existing = Major.query.filter_by(name=name, faculty_id=faculty_id).first()
        if existing:
            skipped += 1
            continue

        prefix = generate_prefix_from_name(name)
        major = Major(name=name, prefix=prefix, faculty_id=faculty_id)
        db.session.add(major)
        added += 1

    db.session.commit()

    return jsonify({
        "message": f"{added} chuyên ngành đã được thêm thành công, {skipped} chuyên ngành bị bỏ qua vì đã tồn tại!",
        "added": added,
        "skipped": skipped
    }), 201


@major_bp.route('/import/majors', methods=['POST'])
@role_required(['Admin'])
def import_majors_api():
    if 'file' not in request.files:
        return jsonify({'message': 'Không tìm thấy file'}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.xlsx'):
        return jsonify({'message': 'Tên file không hợp lệ hoặc không phải định dạng .xlsx'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join('tmp', filename)
    os.makedirs('tmp', exist_ok=True)
    file.save(filepath)

    try:
        df = pd.read_excel(filepath)
        added, skipped, missing_faculty = 0, 0, 0

        for _, row in df.iterrows():
            faculty_name = row.get('Faculty Name')
            major_name = row.get('Major Name')
            if not faculty_name or not major_name:
                continue

            faculty = Faculty.query.filter_by(name=faculty_name).first()
            if not faculty:
                missing_faculty += 1
                continue

            exists = Major.query.filter_by(name=major_name, faculty_id=faculty.id).first()
            if exists:
                skipped += 1
                continue

            prefix = generate_prefix_from_name(major_name)
            major = Major(name=major_name, prefix=prefix, faculty_id=faculty.id)
            db.session.add(major)
            added += 1

        db.session.commit()
        os.remove(filepath)

        return jsonify({
            'message': 'Import chuyên ngành hoàn tất',
            'added': added,
            'skipped (tồn tại)': skipped,
            'missing_faculty': missing_faculty
        }), 200

    except Exception as e:
        os.remove(filepath)
        return jsonify({'message': f'Lỗi xử lý file: {str(e)}'}), 500
