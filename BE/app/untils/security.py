import bcrypt

def hash_password(password):
    """
    Mã hóa mật khẩu sử dụng bcrypt
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    """
    Kiểm tra mật khẩu nhập vào có khớp với mật khẩu đã lưu hay không
    """
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)