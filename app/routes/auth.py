from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Users,Student, Instructor, UserRole, Role,Faculty,Major
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token,get_jwt_identity
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt
import re
import random
from flask_mail import Message
from app.extensions import mail, db

reset_codes = {}
auth_bp = Blueprint('auth', __name__)
BLACKLIST = set()
SCHOOL_EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@daihocnguyentrai\.edu\.vn$'
# SCHOOL_EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    print("Email nhận được:", email)
    print("Password nhận được:", password)

    if not re.match(SCHOOL_EMAIL_REGEX, email):
        return jsonify({'error': 'Chỉ chấp nhận email sinh viên do trường cấp'}), 403

    user = Users.query.filter_by(email=email).first()
    if not user:
        print("Không tìm thấy người dùng!")
        return jsonify({'error': 'Không tìm thấy tài khoản'}), 401

    print("Mật khẩu trong DB:", user.password)

    if not check_password_hash(user.password, password):
        print("Mật khẩu không khớp!")
        return jsonify({'error': 'Mật khẩu không đúng'}), 401

    access_token = create_access_token(identity=str(user.id))

    # Nếu là lần đầu đăng nhập, yêu cầu đổi mật khẩu
    if user.first_login:
        return jsonify({
            'access_token': access_token,
            'first_login': True,
            'message': 'Đăng nhập lần đầu. Vui lòng đổi mật khẩu.'
        })

    return jsonify({'access_token': access_token, 'first_login': False})


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone', None)

    # 1 Kiểm tra email có đúng định dạng không
    if not re.match(SCHOOL_EMAIL_REGEX, email):
        return jsonify({'error': 'Chỉ chấp nhận email sinh viên do trường cấp'}), 400

    # 2️ Kiểm tra email đã tồn tại chưa
    if Users.query.filter_by(email=email).first():
        return jsonify({'error': 'Email đã được sử dụng'}), 400

    # 3️ Kiểm tra độ dài mật khẩu (ít nhất 6 ký tự)
    if len(password) < 6:
        return jsonify({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}), 400

    # 4️ Mã hóa mật khẩu
    hashed_password = generate_password_hash(password)

    # 5️ Tạo user mới
    new_user = Users(email=email, password=hashed_password, name=name, phone=phone)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Tạo tài khoản thành công'}), 


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Lấy JWT ID (jti) của token hiện tại
    jti = get_jwt()["jti"]
    
    # Thêm jti vào danh sách blacklist
    from app.extensions import BLACKLIST
    BLACKLIST.add(jti)

    return jsonify({"message": "Đăng xuất thành công"}), 200

# đăng nhập lần đầu phải đổi mk
@auth_bp.route('/change-password-first-time', methods=['POST'])
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



# gửi gmail
@auth_bp.route('/send-email', methods=['POST']) 
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
@auth_bp.route('/reset-password', methods=['POST'])
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
@auth_bp.route('/change-password', methods=['POST'])
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

@auth_bp.route('/me', methods=['GET'])
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

