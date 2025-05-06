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

    return jsonify({'message': 'Tạo tài khoản thành công'}), 201


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Lấy JWT ID (jti) của token hiện tại
    jti = get_jwt()["jti"]
    
    # Thêm jti vào danh sách blacklist
    from app.extensions import BLACKLIST
    BLACKLIST.add(jti)

    return jsonify({"message": "Đăng xuất thành công"}), 200

