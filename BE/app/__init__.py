# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, jwt
from app.controllers.auth import auth_bp
from app.controllers.api.admin.admin import admin_bp
from app.controllers.api.instructor.profile import instructor_bp
from app.controllers.api.student.profile import student_bp
from app.extensions import mail
from app.controllers.api.admin.faculty_management import admin_faculty_bp
from app.controllers.api.admin.major_management import admin_major_bp
from app.controllers.api.admin.role_management import admin_role_bp
from app.controllers.api.admin.user_management import admin_user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo các extension
    db.init_app(app)
    jwt.init_app(app)

    # Đăng ký các blueprint
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_role_bp, url_prefix="/api/role")
    # app.register_blueprint(course_bp, url_prefix="/api/course")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(instructor_bp, url_prefix="/api/instructor")
    app.register_blueprint(admin_faculty_bp, url_prefix="/api/faculty")
    app.register_blueprint(admin_major_bp, url_prefix="/api/major")
    app.register_blueprint(admin_user_bp, url_prefix="/api/user")

    mail.init_app(app)
    return app
    