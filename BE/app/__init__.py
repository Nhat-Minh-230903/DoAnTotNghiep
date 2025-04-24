# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, jwt
from app.controllers.auth import auth_bp
from app.controllers.api.admin import admin_bp
from app.controllers.api.role import role_bp
from app.controllers.api.course import course_bp
from app.controllers.api.instructor import instructor_bq
from app.controllers.api.student import student_bq
from app.extensions import mail
from app.controllers.api.faculty import faculty_bp
from app.controllers.api.major import major_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo các extension
    db.init_app(app)
    jwt.init_app(app)

    # Đăng ký các blueprint
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(role_bp, url_prefix="/api/role")
    app.register_blueprint(course_bp, url_prefix="/api/course")
    app.register_blueprint(student_bq, url_prefix="/api/student")
    app.register_blueprint(instructor_bq, url_prefix="/api/instructor")
    app.register_blueprint(faculty_bp, url_prefix="/api/faculty")
    app.register_blueprint(major_bp, url_prefix="/api/major")

    mail.init_app(app)
    return app
    