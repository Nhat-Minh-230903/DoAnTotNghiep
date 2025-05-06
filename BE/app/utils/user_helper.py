from app import db
from app.models.user import Instructor, Student
from functools import wraps 
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from app.models.user import Role, UserRole
import unicodedata
import re

# Hàm tạo mã giảng viên
def generate_instructor_id(faculty_id, stt):
    faculty_code = str(faculty_id).zfill(2)
    stt_code = str(stt).zfill(4)
    return f"GV{faculty_code}{stt_code}"

# Hàm tạo email giảng viên
def generate_instructor_email(employee_id):
    return f"{employee_id}@daihocnguyentrai.edu.vn"

# Hàm lấy STT tiếp theo theo faculty
def get_next_instructor_stt(faculty_id):
    faculty_code = str(faculty_id).zfill(2)
    existing_ids = db.session.query(Instructor.employee_id).all()
    filtered = [
        int(eid[0][len("GV" + faculty_code):])
        for eid in existing_ids
        if eid[0].startswith(f"GV{faculty_code}")
    ]
    return max(filtered) + 1 if filtered else 1

# Hàm tạo student_id từ năm nhập học, ngành, khoa và STT
def generate_student_id(enrollment_year, faculty_id, major_id, stt):
    year_suffix = str(enrollment_year)[-2:]
    faculty_code = str(faculty_id).zfill(2)
    major_code = str(major_id).zfill(2)
    stt_code = str(stt).zfill(4)
    return f"{year_suffix}{faculty_code}{major_code}{stt_code}"

# Hàm tạo email sinh viên từ student_id
def generate_student_email(student_id):
    return f"{student_id}@daihocnguyentrai.edu.vn"

def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()

            user_role = (
                db.session.query(Role.name)
                .join(UserRole, Role.id == UserRole.role_id)
                .filter(UserRole.user_id == user_id)
                .first()
            )

            role_name = user_role[0].lower() if user_role else None

            if role_name not in [r.lower() for r in allowed_roles]:
                return jsonify({'error': 'Bạn không có quyền truy cập'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def normalize_text(text):
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')  # bỏ dấu
    text = re.sub(r'\s+', ' ', text)  # bỏ khoảng trắng thừa
    return text

def get_faculty_id_by_name(name, faculties_map):
    return faculties_map.get(normalize_text(name))

def get_major_id_by_name(name, majors_map):
    return majors_map.get(normalize_text(name))