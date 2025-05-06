import os
import pandas as pd     
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app.utils.user_helper import role_required
from app.models.user import Users, Faculty, Major
from app import db
from app.utils.course_helper import generate_prefix_from_name
from werkzeug.utils import secure_filename
from io import BytesIO

admin_faculty_bp = Blueprint('admin_faculty_bp', __name__)

#Thêm từ excel thêm ngành và chuyên ngành/ngành riêng
#Thêm sửa xóa hiển thị

@admin_faculty_bp.route('/import/faculty-majors', methods=['POST'])
@role_required(['Admin'])
def import_faculty_and_majors():
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
        added_faculty, added_major, skipped_major = 0, 0, 0

        for _, row in df.iterrows():
            faculty_name = row.get('Faculty Name')
            major_name = row.get('Major Name')
            if not faculty_name or not major_name:
                continue

            # Thêm hoặc tìm faculty
            faculty = Faculty.query.filter_by(name=faculty_name).first()
            if not faculty:
                faculty = Faculty(name=faculty_name, prefix=generate_prefix_from_name(faculty_name))
                db.session.add(faculty)
                db.session.flush()  # để lấy faculty.id ngay lập tức
                added_faculty += 1

            # Thêm major nếu chưa có
            existing_major = Major.query.filter_by(name=major_name, faculty_id=faculty.id).first()
            if existing_major:
                skipped_major += 1
                continue

            prefix = generate_prefix_from_name(major_name)
            major = Major(name=major_name, prefix=prefix, faculty_id=faculty.id)
            db.session.add(major)
            added_major += 1

        db.session.commit()
        os.remove(filepath)

        return jsonify({
            'message': 'Import ngành và chuyên ngành hoàn tất',
            'added_faculty': added_faculty,
            'added_major': added_major,
            'skipped_major (tồn tại)': skipped_major
        }), 200

    except Exception as e:
        os.remove(filepath)
        return jsonify({'message': f'Lỗi xử lý file: {str(e)}'}), 500
    

# Kiểm tra trùng lặp tên ngành
def is_duplicate_faculty_name(name, exclude_id=None):
    query = Faculty.query.filter(Faculty.name == name)
    if exclude_id is not None:
        query = query.filter(Faculty.id != exclude_id)
    return db.session.query(query.exists()).scalar()

# đã test
@admin_faculty_bp.route('', methods=['GET'])
@role_required(['Admin'])
def get_all_faculty():
    faculty=Faculty.query.all()
    data = [{
        'id':c.id,
        'name':c.name,
        'prefix':c.prefix
    }for c in faculty]
    return jsonify(data)


@admin_faculty_bp.route('', methods=['POST'])
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


@admin_faculty_bp.route('/<int:id>', methods=['PUT'])
@role_required(['Admin'])
def update_faculty(id):
    data = request.get_json()
    name = data.get('name')

    faculty = Faculty.query.get(id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    # ⚠️ Check nếu tên không thay đổi
    if faculty.name == name:
        return jsonify({"error": "Tên ngành chưa được thay đổi!"}), 400

    # Check trùng lặp tên ngành khác
    if is_duplicate_faculty_name(name, exclude_id=id):
        return jsonify({"error": "Ten  ngành đã tồn tại!"}), 400

    faculty.name = name
    faculty.prefix = generate_prefix_from_name(name)
    db.session.commit()

    return jsonify({"message": "Faculty updated successfully"}), 200




@admin_faculty_bp.route('/<int:id>', methods=['DELETE'])
@role_required(['Admin'])
def delete_faculty(id):
    faculty = Faculty.query.get(id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404
    
    db.session.delete(faculty)
    db.session.commit()
    
    return jsonify({"message": "Faculty deleted successfully"}), 200


@admin_faculty_bp.route('/import', methods=['POST'])
@role_required(['Admin'])
def import_faculties_api():
    if 'file' not in request.files:
        return jsonify({'message': 'Không tìm thấy file'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'Tên file không hợp lệ'}), 400

    if not file.filename.endswith('.xlsx'):
        return jsonify({'message': 'Chỉ chấp nhận file .xlsx'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join('tmp', filename)
    os.makedirs('tmp', exist_ok=True)
    file.save(filepath)

    try:
        df = pd.read_excel(filepath)

        added = 0
        skipped = 0

        for index, row in df.iterrows():
            name = row.get('Faculty Name')
            if not name:
                continue

            existing = Faculty.query.filter_by(name=name).first()
            if existing:
                skipped += 1
                continue

            prefix = generate_prefix_from_name(name)
            faculty = Faculty(name=name, prefix=prefix)
            db.session.add(faculty)
            added += 1

        db.session.commit()
        os.remove(filepath)

        return jsonify({
            'message': 'Import thành công',
            'added': added,
            'skipped (tồn tại)': skipped
        }), 200

    except Exception as e:
        os.remove(filepath)
        return jsonify({'message': f'Lỗi xử lý file: {str(e)}'}), 500