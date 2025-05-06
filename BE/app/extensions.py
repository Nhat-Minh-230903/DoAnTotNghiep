
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail

# Tạo một đối tượng duy nhất cho SQLAlchemy và JWTManager
db = SQLAlchemy()
jwt = JWTManager()

# Danh sách token đã bị blacklist
BLACKLIST = set()

# Kiểm tra nếu token có bị blacklist không
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST

mail = Mail()