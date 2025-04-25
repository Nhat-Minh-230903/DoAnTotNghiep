import bcrypt
import pandas as pd
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from app.models.user import Users, Student, Instructor, UserRole, Role, Faculty, Major
from app import db
from werkzeug.security import generate_password_hash
from datetime import datetime
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
import random
from flask_mail import Message
from app.extensions import mail, db
from werkzeug.utils import secure_filename
import os
from app.utils.course_helper import generate_prefix_from_name

admin_bp = Blueprint('admin_bp', __name__)

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

@admin_bp.route('/upload-student-list', methods=['POST'])
def upload_student_list():
    if 'file' not in request.files:
        return jsonify({'error': 'Chưa tải file'}), 400

    file = request.files['file']

    try:
        df = pd.read_excel(file)
    except Exception as e:
        return jsonify({'error': f"Lỗi khi đọc file: {str(e)}"}), 500

    # Các cột bắt buộc
    required_columns = ['STT', 'Tên', 'Ngày tháng năm sinh', 'CCCD', 'Faculty', 'Major', 'Enrollment Year', 'SĐT', 'Giới tính', 'Địa chỉ']
    for column in required_columns:
        if column not in df.columns:
            return jsonify({'error': f"Cột '{column}' không tồn tại trong file Excel"}), 400

    faculties_dict = {f.name: f.id for f in Faculty.query.all()}
    majors_dict = {m.name: m.id for m in Major.query.all()}

    success_results = []
    error_results = []
    existing_emails = set()

    gender_map = {
        'nam': 'male',
        'nữ': 'female',
        'nu': 'female',
        'khác': 'other',
        'other': 'other'
    }

    for index, row in df.iterrows():
        try:
            name = row['Tên']
            dob = row['Ngày tháng năm sinh']
            cccd = str(row['CCCD']).strip()
            faculty_name = row['Faculty']
            major_name = row['Major']
            enrollment_year = str(row['Enrollment Year']).strip()
            phone = str(row['SĐT']).strip()
            stt = row['STT']
            address = str(row['Địa chỉ']).strip()
            gender_raw = str(row['Giới tính']).strip().lower()
            gender = gender_map.get(gender_raw, 'other')

            faculty_id = faculties_dict.get(faculty_name)
            major_id = majors_dict.get(major_name)

            if not faculty_id or not major_id:
                error_results.append(f"Không tìm thấy ID cho Faculty: {faculty_name}, Major: {major_name}")
                continue

            if isinstance(dob, str):
                try:
                    dob = datetime.strptime(dob, '%d/%m/%Y').date()
                except ValueError:
                    error_results.append(f"Không thể chuyển đổi ngày sinh cho {name}: {dob}")
                    continue

            student_id = generate_student_id(enrollment_year, major_id, faculty_id, stt)
            email = generate_student_email(student_id)

            if db.session.query(Users).filter_by(email=email).first():
                error_results.append(f"Email {email} đã tồn tại trong hệ thống")
                continue

            if email in existing_emails:
                error_results.append(f"Email {email} bị trùng trong file Excel")
                continue

            existing_emails.add(email)

            if db.session.query(Student).filter_by(student_id=student_id).first():
                error_results.append(f"Student ID {student_id} đã tồn tại trong hệ thống")
                continue

            hashed_password = generate_password_hash(cccd)

            user = Users(
                email=email,
                password=hashed_password,
                name=name,
                phone=phone,
                birth=dob,
                first_login=True,
                gender=gender,
                address=address
            )
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                student_id=student_id,
                faculty_id=faculty_id,
                major_id=major_id,
                enrollment_year=enrollment_year,
            )
            db.session.add(student)

            db.session.commit()

            success_results.append({
                'STT': len(success_results) + 1,
                'Tên': name,
                'Gmail': email
            })

        except Exception as e:
            db.session.rollback()
            error_results.append(f"Lỗi xử lý sinh viên {name if 'name' in locals() else '[Không rõ]'}: {str(e)}")

    # Tạo file Excel trả về
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if success_results:
            success_df = pd.DataFrame(success_results)
            success_df.to_excel(writer, sheet_name='Danh sách sinh viên', index=False)

        if error_results:
            error_df = pd.DataFrame({'Lỗi': error_results})
            error_df.to_excel(writer, sheet_name='Lỗi', index=False)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name='danh_sach_sinh_vien_hoan_tra.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

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

@admin_bp.route('/upload-instructor-list', methods=['POST'])
def upload_instructor_list():
    if 'file' not in request.files:
        return jsonify({'error': 'Chưa tải file'}), 400

    file = request.files['file']

    try:
        df = pd.read_excel(file)
    except Exception as e:
        return jsonify({'error': f"Lỗi khi đọc file: {str(e)}"}), 500

    required_columns = [
        'STT', 'Tên', 'Ngày tháng năm sinh', 'CCCD', 'Faculty',
        'SĐT', 'Giới tính', 'Địa chỉ', 'Vị trí', 'Học vị', 'Năm vào'
    ]
    for column in required_columns:
        if column not in df.columns:
            return jsonify({'error': f"Cột '{column}' không tồn tại trong file Excel"}), 400

    faculties_dict = {f.name: f.id for f in Faculty.query.all()}
    success_results = []
    error_results = []
    existing_emails = set()
    faculty_stt_map = {}

    gender_map = {
        'nam': 'male',
        'nữ': 'female',
        'nu': 'female',
        'khác': 'other',
        'other': 'other'
    }

    for index, row in df.iterrows():
        try:
            name = row['Tên']
            dob = row['Ngày tháng năm sinh']
            cccd = str(row['CCCD']).strip()
            faculty_name = row['Faculty']
            phone = str(row['SĐT']).strip()
            gender_raw = str(row['Giới tính']).strip().lower()
            address = str(row['Địa chỉ']).strip()
            position = str(row['Vị trí']).strip()
            degree = str(row['Học vị']).strip()
            joined_year_raw = row['Năm vào']
            joined_year = str(int(joined_year_raw)) if pd.notnull(joined_year_raw) else None

            gender = gender_map.get(gender_raw, 'other')

            faculty_id = faculties_dict.get(faculty_name)
            if not faculty_id:
                error_results.append(f"Khoa không hợp lệ: {faculty_name}")
                continue

            # Xử lý ngày sinh
            if isinstance(dob, str):
                try:
                    dob = datetime.strptime(dob, '%d/%m/%Y').date()
                except ValueError:
                    error_results.append(f"Không thể chuyển đổi ngày sinh cho {name}: {dob}")
                    continue

            # Lấy STT kế tiếp theo khoa
            if faculty_id not in faculty_stt_map:
                faculty_stt_map[faculty_id] = get_next_instructor_stt(faculty_id)

            next_stt = faculty_stt_map[faculty_id]
            faculty_stt_map[faculty_id] += 1

            # Tạo mã nhân viên và email
            employee_id = generate_instructor_id(faculty_id, next_stt)
            email = generate_instructor_email(employee_id)

            if db.session.query(Users).filter_by(email=email).first():
                error_results.append(f"Email {email} đã tồn tại trong hệ thống")
                continue

            if db.session.query(Instructor).filter_by(employee_id=employee_id).first():
                error_results.append(f"Mã nhân viên {employee_id} đã tồn tại")
                continue

            if email in existing_emails:
                error_results.append(f"Email {email} bị trùng trong file Excel")
                continue

            existing_emails.add(email)

            hashed_password = generate_password_hash(cccd)

            user = Users(
                email=email,
                password=hashed_password,
                name=name,
                phone=phone,
                birth=dob,
                gender=gender,
                address=address,
                first_login=True
            )
            db.session.add(user)
            db.session.flush()

            instructor = Instructor(
                user_id=user.id,
                employee_id=employee_id,
                position=position,
                degree=degree,
                faculty_id=faculty_id,
                joined_year=joined_year
            )
            db.session.add(instructor)

            db.session.commit()

            success_results.append({
                'STT': len(success_results) + 1,
                'Tên': name,
                'Gmail': email
            })

        except Exception as e:
            db.session.rollback()
            error_results.append(f"Lỗi xử lý giảng viên {name if 'name' in locals() else '[Không rõ]'}: {str(e)}")

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if success_results:
            pd.DataFrame(success_results).to_excel(writer, sheet_name='Danh sách giảng viên', index=False)
        if error_results:
            pd.DataFrame({'Lỗi': error_results}).to_excel(writer, sheet_name='Lỗi', index=False)

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='ket_qua_upload_giang_vien.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

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

# Lấy tất cả các user theo vai trò
@admin_bp.route('/users', methods=['GET'])
@role_required(['Admin'])  # Chỉ admin được phép truy cập
def get_users():
    role_filter = request.args.get('role')

    users = Users.query.all()
    user_list = []

    for user in users:
        # Lấy role
        user_role = (
            db.session.query(Role.name)
            .join(UserRole, Role.id == UserRole.role_id)
            .filter(UserRole.user_id == user.id)
            .first()
        )
        role = user_role[0] if user_role else "Không có"

        # Lọc nếu có yêu cầu ?role=
        if role_filter:
            if role_filter.lower() == 'student' and not Student.query.filter_by(user_id=user.id).first():
                continue
            if role_filter.lower() == 'instructor' and not Instructor.query.filter_by(user_id=user.id).first():
                continue

        # Thông tin cơ bản
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'birth': user.birth,
            'gender': user.gender,
            'address': user.address,
            'status': user.status,
            'first_login': user.first_login,
            'created_at': user.created_at,
            'role': role
        }

        # Thông tin sinh viên nếu có
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            faculty = Faculty.query.get(student.faculty_id)
            major = Major.query.get(student.major_id)
            user_data['student_info'] = {
                'student_id': student.student_id,
                'faculty': faculty.name if faculty else None,
                'major': major.name if major else None,
                'enrollment_year': student.enrollment_year
            }

        # Thông tin giảng viên nếu có
        instructor = Instructor.query.filter_by(user_id=user.id).first()
        if instructor:
            faculty = Faculty.query.get(instructor.faculty_id)
            user_data['instructor_info'] = {
                'employee_id': instructor.employee_id,
                'faculty': faculty.name if faculty else None,
                'position': instructor.position,
                'degree': instructor.degree,
                'joined_year': instructor.joined_year
            }

        user_list.append(user_data)

    return jsonify({'users': user_list}), 200


@admin_bp.route('/update_users/<int:user_id>', methods=['PUT'])
@role_required(['Admin'])  # Chỉ admin được quyền cập nhật
def update_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404

    data = request.get_json()

    # --- CẬP NHẬT THÔNG TIN NGƯỜI DÙNG CƠ BẢN ---
    if 'name' in data and data['name'].strip():
        user.name = data['name']

    if 'email' in data and data['email'].strip():
        existing_email = Users.query.filter(Users.email == data['email'], Users.id != user.id).first()
        if existing_email:
            return jsonify({'error': 'Email đã được sử dụng'}), 400
        user.email = data['email']

    if 'phone' in data and data['phone'].strip():
        user.phone = data['phone']

    if 'birth' in data and data['birth'].strip():
        user.birth = data['birth']

    if 'gender' in data and data['gender'].strip():
        user.gender = data['gender']

    if 'address' in data and data['address'].strip():
        user.address = data['address']

    if 'status' in data and data['status'].strip():
        user.status = data['status']

    if 'password' in data and data['password'].strip():
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.password = hashed_password

    # --- CẬP NHẬT THÔNG TIN SINH VIÊN ---
    student = Student.query.filter_by(user_id=user.id).first()
    if student:
        if 'student_id' in data and data['student_id'].strip():
            student.student_id = data['student_id']

        if 'faculty_id' in data:
            faculty = Faculty.query.get(data['faculty_id'])
            if not faculty:
                return jsonify({'error': 'Khoa không tồn tại'}), 400
            student.faculty_id = data['faculty_id']

        if 'major_id' in data:
            major = Major.query.get(data['major_id'])
            if not major:
                return jsonify({'error': 'Ngành học không tồn tại'}), 400
            student.major_id = data['major_id']

        if 'enrollment_year' in data and data['enrollment_year'].strip():
            student.enrollment_year = data['enrollment_year']

    # --- CẬP NHẬT THÔNG TIN GIẢNG VIÊN ---
    instructor = Instructor.query.filter_by(user_id=user.id).first()
    if instructor:
        if 'employee_id' in data and data['employee_id'].strip():
            instructor.employee_id = data['employee_id']

        if 'faculty_id' in data:
            faculty = Faculty.query.get(data['faculty_id'])
            if not faculty:
                return jsonify({'error': 'Khoa không tồn tại'}), 400
            instructor.faculty_id = data['faculty_id']

        if 'position' in data and data['position'].strip():
            instructor.position = data['position']

        if 'degree' in data and data['degree'].strip():
            instructor.degree = data['degree']

        if 'joined_year' in data and data['joined_year'].strip():
            instructor.joined_year = data['joined_year']

    db.session.commit()

    return jsonify({'message': 'Cập nhật người dùng thành công'}), 200

# xóa cứng 1 bản xóa vĩnh viên
@admin_bp.route('/delete_users/<int:user_id>', methods=['DELETE'])
@role_required(['Admin'])  # Chỉ admin được phép xoá
def delete_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'error': 'Người dùng không tồn tại'}), 404

    # Xoá nếu là sinh viên
    student = Student.query.filter_by(user_id=user.id).first()
    if student:
        db.session.delete(student)

    # Xoá nếu là giảng viên
    instructor = Instructor.query.filter_by(user_id=user.id).first()
    if instructor:
        db.session.delete(instructor)

    # Xoá các vai trò liên kết (nếu dùng bảng trung gian)
    UserRole.query.filter_by(user_id=user.id).delete()

    # Xoá người dùng chính
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Xoá người dùng thành công'}), 200


# xóa mềm , xóa tạm thời có thể khôi phục
@admin_bp.route('/soft_delete_user/<int:user_id>', methods=['DELETE'])
@role_required(['Admin'])  # Chỉ admin được phép xoá
def soft_delete_user(user_id):
    user = Users.query.get(user_id)
    if not user or user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc đã bị xoá'}), 404

    # Gán cờ xoá mềm
    user.is_deleted = True

    # Nếu muốn "ngắt kết nối" tài khoản:
    user.status = 'inactive'  # Tùy vào logic hệ thống

    db.session.commit()
    return jsonify({'message': 'Người dùng đã bị xoá (soft delete)'}), 200

# Khôi phục người dùng
@admin_bp.route('/restore_user/<int:user_id>', methods=['PUT'])
@role_required(['Admin'])
def restore_user(user_id):
    user = Users.query.get(user_id)
    if not user or not user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc chưa bị xoá'}), 404

    user.is_deleted = False
    user.status = 'active'
    db.session.commit()

    return jsonify({'message': 'Khôi phục người dùng thành công'}), 200

# lấy role của người dùng , chỉ có admin hoặc người dùng đó mới lấy đc
@admin_bp.route('/get_user_roles/<int:user_id>', methods=['GET'])
@jwt_required()

def get_user_roles(user_id):

    
    # Chỉ cho phép admin hoặc chính người dùng đó xem role
    current_user_id = get_jwt_identity()
    current_user_roles = (
        db.session.query(Role.name)
        .join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == current_user_id)
        .all()
    )
    current_user_roles = [r[0] for r in current_user_roles]

    if current_user_id != user_id and 'Admin' not in current_user_roles:
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
# chỉ định role cho 1 người dùng
@admin_bp.route('/assign_role_to_user/<int:user_id>', methods=['POST'])
@role_required(['Admin'])  # Chỉ admin có quyền gán role
def assign_role_to_user(user_id):
    data = request.get_json()
    role_id = data.get('role_id')

    if not role_id:
        return jsonify({'error': 'Thiếu role_id'}), 400

    # Kiểm tra user tồn tại
    user = Users.query.get(user_id)
    if not user or user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc đã bị xoá'}), 404

    # Kiểm tra role tồn tại
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Vai trò không tồn tại'}), 404

    # Kiểm tra nếu role đã được gán rồi
    existing = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if existing:
        return jsonify({'message': 'Người dùng đã có vai trò này'}), 200

    # Gán role
    new_user_role = UserRole(user_id=user_id, role_id=role_id)
    db.session.add(new_user_role)
    db.session.commit()

    return jsonify({'message': 'Gán vai trò thành công'}), 201

# xóa role  cho 1 người dùng 
@admin_bp.route('/remove_role_from_user/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@role_required(['Admin'])  # Chỉ admin được phép gỡ role
def remove_role_from_user(user_id, role_id):
    # Kiểm tra user tồn tại
    user = Users.query.get(user_id)
    if not user or user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc đã bị xoá'}), 404

    # Kiểm tra role tồn tại
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Vai trò không tồn tại'}), 404

    # Kiểm tra user có role đó không
    user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if not user_role:
        return jsonify({'message': 'Người dùng không có vai trò này'}), 200

    # Xoá role khỏi user
    db.session.delete(user_role)
    db.session.commit()

    return jsonify({'message': 'Gỡ vai trò khỏi người dùng thành công'}), 200


# đăng nhập lần đầu phải đổi mk
@admin_bp.route('/change-password-first-time', methods=['POST'])
@jwt_required()
def change_password_first_time():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_password = data.get('new_password')

    user = Users.query.get(current_user_id)
    user.password = generate_password_hash(new_password)
    user.first_login = False  # Đã đổi mật khẩu
    db.session.commit()

    return jsonify({'message': 'Đổi mật khẩu thành công'})

reset_codes = {}
# gửi gmail
@admin_bp.route('/send-email', methods=['POST']) 
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Không tìm thấy email"}), 404

    code = str(random.randint(100000, 999999))
    reset_codes[email] = code

    # Gửi email
    msg = Message("Mã khôi phục mật khẩu", recipients=[email])
    msg.body = f"Mã xác nhận của bạn là: {code}"
    mail.send(msg)

    return jsonify({"message": "Mã xác nhận đã được gửi đến email"}), 200

# thay doi mk khi chua dang nhap --> phai gui gmail de lay ma
@admin_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("new_password")

    if reset_codes.get(email) != code:
        return jsonify({"error": "Mã xác nhận không đúng"}), 400

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404

    user.password = generate_password_hash(new_password)
    db.session.commit()
    reset_codes.pop(email)  # Xóa mã sau khi dùng

    return jsonify({"message": "Đổi mật khẩu thành công"}), 201


# đôi mk khi đã đăng nhập
@admin_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():

    user_id = get_jwt_identity()
    user = Users.query.get(user_id)

    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not check_password_hash(user.password, old_password):
        return jsonify({"error": "Mật khẩu cũ không đúng"}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Đổi mật khẩu thành công"}), 200




@admin_bp.route('/import/faculty-majors', methods=['POST'])
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
