import pandas as pd
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from datetime import datetime
from werkzeug.security import generate_password_hash
import bcrypt
from app.models.user import Users, Student, Instructor, Faculty, Major,UserRole,Role
from app import db
from app.utils.user_helper import normalize_text
from app.utils.user_helper import role_required
from app.utils.user_helper import (
    generate_instructor_id, generate_student_id,
    generate_instructor_email, generate_student_email,
    get_next_instructor_stt
)

admin_user_bp = Blueprint('admin_user_bp', __name__)

GENDER_MAP = {
    'nam': 'male',
    'nữ': 'female',
    'nu': 'female',
    'khác': 'other',
    'other': 'other'
}

def parse_date(value):
    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), '%d/%m/%Y').date()
        except ValueError:
            return None
    if isinstance(value, datetime):
        return value.date()
    return None

def validate_columns(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return f"Các cột bị thiếu trong file Excel: {', '.join(missing)}"
    return None

def prepare_excel_response(success_results, error_results, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if success_results:
            pd.DataFrame(success_results).to_excel(writer, sheet_name='Thành công', index=False)
        if error_results:
            pd.DataFrame({'Lỗi': error_results}).to_excel(writer, sheet_name='Lỗi', index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@admin_user_bp.route('/upload-instructor-list', methods=['POST'])
def upload_instructor_list():
    if 'file' not in request.files:
        return jsonify({'error': 'Chưa tải file'}), 400

    try:
        df = pd.read_excel(request.files['file'])
    except Exception as e:
        return jsonify({'error': f"Lỗi khi đọc file Excel: {str(e)}"}), 500

    required_columns = ['STT', 'Tên', 'Ngày tháng năm sinh', 'CCCD', 'Faculty', 'SĐT', 'Giới tính', 'Địa chỉ', 'Vị trí', 'Học vị', 'Năm vào']
    error_msg = validate_columns(df, required_columns)
    if error_msg:
        return jsonify({'error': error_msg}), 400

    faculties = {normalize_text(f.name): f.id for f in Faculty.query.all()}
    faculty_stt_map = {}
    success_results, error_results, emails_in_file = [], [], set()

    for _, row in df.iterrows():
        try:
            name = str(row['Tên']).strip()
            dob = parse_date(row['Ngày tháng năm sinh'])
            cccd = str(row['CCCD']).strip()
            faculty_name = normalize_text(row['Faculty'])
            phone = str(row['SĐT']).strip()
            gender = GENDER_MAP.get(str(row['Giới tính']).strip().lower(), 'other')
            address = str(row['Địa chỉ']).strip()
            position = str(row['Vị trí']).strip()
            degree = str(row['Học vị']).strip()
            joined_year = str(int(row['Năm vào'])) if pd.notnull(row['Năm vào']) else None

            faculty_id = faculties.get(faculty_name)
            if not faculty_id:
                error_results.append(f"Khoa không hợp lệ: {row['Faculty']}")
                continue
            if not dob:
                error_results.append(f"Không thể chuyển đổi ngày sinh cho {name}")
                continue

            if faculty_id not in faculty_stt_map:
                faculty_stt_map[faculty_id] = get_next_instructor_stt(faculty_id)
            next_stt = faculty_stt_map[faculty_id]
            faculty_stt_map[faculty_id] += 1

            employee_id = generate_instructor_id(faculty_id, next_stt)
            email = generate_instructor_email(employee_id)

            if email in emails_in_file or Users.query.filter_by(email=email).first() or Instructor.query.filter_by(employee_id=employee_id).first():
                error_results.append(f"Email hoặc mã nhân viên đã tồn tại: {email}")
                continue
            emails_in_file.add(email)

            hashed_password = generate_password_hash(cccd)

            user = Users(
                email=email, password=hashed_password, name=name,
                phone=phone, birth=dob, gender=gender,
                address=address, first_login=True
            )
            db.session.add(user)
            db.session.flush()

            instructor = Instructor(
                user_id=user.id, employee_id=employee_id,
                position=position, degree=degree,
                faculty_id=faculty_id, joined_year=joined_year
            )
            db.session.add(instructor)
            db.session.commit()

            success_results.append({'STT': len(success_results) + 1, 'Tên': name, 'Gmail': email})
        except Exception as e:
            db.session.rollback()
            error_results.append(f"Lỗi giảng viên {name if 'name' in locals() else '[Không rõ]'}: {str(e)}")

    return prepare_excel_response(success_results, error_results, 'ket_qua_upload_giang_vien.xlsx')


@admin_user_bp.route('/upload-student-list', methods=['POST'])
def upload_student_list():
    if 'file' not in request.files:
        return jsonify({'error': 'Chưa tải file'}), 400

    try:
        df = pd.read_excel(request.files['file'])
    except Exception as e:
        return jsonify({'error': f"Lỗi khi đọc file Excel: {str(e)}"}), 500

    required_columns = ['STT', 'Tên', 'Ngày tháng năm sinh', 'CCCD', 'Faculty', 'Major',
                        'Enrollment Year', 'SĐT', 'Giới tính', 'Địa chỉ']
    error_msg = validate_columns(df, required_columns)
    if error_msg:
        return jsonify({'error': error_msg}), 400

    faculties = {normalize_text(f.name): f.id for f in Faculty.query.all()}
    majors = {normalize_text(m.name): m.id for m in Major.query.all()}
    success_results, error_results, emails_in_file = [], [], set()

    for _, row in df.iterrows():
        try:
            name = str(row['Tên']).strip()
            dob = parse_date(row['Ngày tháng năm sinh'])
            cccd = str(row['CCCD']).strip()
            faculty_name = normalize_text(row['Faculty'])
            major_name = normalize_text(row['Major'])
            enrollment_year = str(row['Enrollment Year']).strip()
            phone = str(row['SĐT']).strip()
            stt = row['STT']
            address = str(row['Địa chỉ']).strip()
            gender = GENDER_MAP.get(str(row['Giới tính']).strip().lower(), 'other')

            faculty_id = faculties.get(faculty_name)
            major_id = majors.get(major_name)
            if not faculty_id or not major_id:
                error_results.append(f"Không tìm thấy Faculty/Major: {row['Faculty']}/{row['Major']}")
                continue
            if not dob:
                error_results.append(f"Không thể chuyển đổi ngày sinh cho {name}")
                continue

            student_id = generate_student_id(enrollment_year, major_id, faculty_id, stt)
            email = generate_student_email(student_id)

            if email in emails_in_file or Users.query.filter_by(email=email).first() or Student.query.filter_by(student_id=student_id).first():
                error_results.append(f"Email hoặc mã sinh viên đã tồn tại: {email}")
                continue
            emails_in_file.add(email)

            hashed_password = generate_password_hash(cccd)

            user = Users(
                email=email, password=hashed_password, name=name,
                phone=phone, birth=dob, gender=gender,
                address=address, first_login=True
            )
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id, student_id=student_id,
                faculty_id=faculty_id, major_id=major_id,
                enrollment_year=enrollment_year
            )
            db.session.add(student)
            db.session.commit()

            success_results.append({'STT': len(success_results) + 1, 'Tên': name, 'Gmail': email})
        except Exception as e:
            db.session.rollback()
            error_results.append(f"Lỗi sinh viên {name if 'name' in locals() else '[Không rõ]'}: {str(e)}")

    return prepare_excel_response(success_results, error_results, 'ket_qua_upload_sinh_vien.xlsx')
# Lấy tất cả các user theo vai trò
@admin_user_bp.route('', methods=['GET'])
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


@admin_user_bp.route('/update_users/<int:user_id>', methods=['PUT'])
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
@admin_user_bp.route('/delete_users/<int:user_id>', methods=['DELETE'])
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
@admin_user_bp.route('/soft_delete_user/<int:user_id>', methods=['DELETE'])
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
@admin_user_bp.route('/restore_user/<int:user_id>', methods=['PUT'])
@role_required(['Admin'])
def restore_user(user_id):
    user = Users.query.get(user_id)
    if not user or not user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc chưa bị xoá'}), 404

    user.is_deleted = False
    user.status = 'active'
    db.session.commit()

    return jsonify({'message': 'Khôi phục người dùng thành công'}), 200