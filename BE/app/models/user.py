from app import db
from datetime import datetime

class Users(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    birth = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False, default='active')
    first_login = db.Column(db.Boolean ,default=False)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, default=False)
    # Mối quan hệ với các bảng khác
    # student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    # instructor = db.relationship('Instructor', backref='user', uselist=False, cascade='all, delete-orphan')
    # roles = db.relationship('Role', secondary='User_Roles', backref=db.backref('users', lazy='dynamic'))
    students = db.relationship('Student', backref='user', lazy=True)

class Faculty(db.Model):
    __tablename__ = 'faculties'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    prefix=db.Column(db.String(10))
class Major(db.Model):
    __tablename__ = 'majors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'), nullable=False)
    prefix=db.Column(db.String(10))

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'), nullable=True)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'), nullable=True)
    enrollment_year = db.Column(db.String(4), nullable=True)

    # Quan hệ
    faculty = db.relationship('Faculty', backref='students')
    major = db.relationship('Major', backref='students')

# 👉 Instructor Model mới
class Instructor(db.Model):
    __tablename__ = 'instructors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=True)
    degree = db.Column(db.String(50), nullable=True)
    joined_year = db.Column(db.String(4), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'), nullable=True)

    faculty = db.relationship('Faculty', backref='instructors')
    
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    permissions = db.relationship('Permission', secondary='role_permissions', backref=db.backref('roles', lazy='dynamic'))

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('role_id', 'permission_id'),)

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id'),)

