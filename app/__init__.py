# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, jwt
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.admin import admin_bp
from app.routes.role import role_bp
from app.extensions import mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo các extension
    db.init_app(app)
    jwt.init_app(app)

    # Đăng ký các blueprint
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(role_bp, url_prefix="/api/role")

    mail.init_app(app)
    return app
    