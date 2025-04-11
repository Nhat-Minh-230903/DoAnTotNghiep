# from app.models.user import User, Role, Permission
# from app.untils import verify_password
# from app import db
# from flask_jwt_extended import create_access_token, create_refresh_token

# class AuthService:
#     def login(self, email, password):
#         """
#         Xử lý đăng nhập và tạo token nếu thông tin đăng nhập chính xác
#         """
#         # Tìm người dùng theo email
#         user = User.query.filter_by(email=email).first()
        
#         # Nếu không tìm thấy người dùng hoặc mật khẩu không khớp
#         if not user or not verify_password(password, user.password):
#             return {
#                 "success": False,
#                 "message": "Email hoặc mật khẩu không chính xác"
#             }
        
#         # Lấy thông tin vai trò và quyền hạn
#         roles = [role.name for role in user.roles]
#         permissions = []
#         for role in user.roles:
#             for permission in role.permissions:
#                 if permission.code not in permissions:
#                     permissions.append(permission.code)
        
#         # Tạo identity cho JWT
#         identity = {
#             "id": user.id,
#             "roles": roles
#         }
        
#         # Tạo access token và refresh token
#         access_token = create_access_token(identity=user.id)
#         refresh_token = create_refresh_token(identity=user.id)
        
#         # Trả về thông tin người dùng và token
#         return {
#             "success": True,
#             "message": "Đăng nhập thành công",
#             "data": {
#                 "user": {
#                     "id": user.id,
#                     "name": user.name,
#                     "email": user.email,
#                     "roles": roles,
#                     "permissions": permissions
#                 },
#                 "tokens": {
#                     "access_token": access_token,
#                     "refresh_token": refresh_token
#                 }
#             }
#         }
    
#     def get_user_info(self, user_id):
#         """
#         Lấy thông tin chi tiết của người dùng
#         """
#         user = User.query.get(user_id)
        
#         if not user:
#             return None
        
#         roles = [role.name for role in user.roles]
#         permissions = []
#         for role in user.roles:
#             for permission in role.permissions:
#                 if permission.code not in permissions:
#                     permissions.append(permission.code)
        
#         # Xác định loại người dùng (sinh viên hoặc giảng viên)
#         user_type = None
#         user_detail = None
        
#         if user.student:
#             user_type = "student"
#             user_detail = {
#                 "student_id": user.student.student_id,
#                 "class": user.student.class_name,
#                 "faculty": user.student.faculty,
#                 "program": user.student.program,
#                 "enrollment_year": user.student.enrollment_year
#             }
#         elif user.instructor:
#             user_type = "instructor"
#             user_detail = {
#                 "employee_id": user.instructor.employee_id,
#                 "department": user.instructor.department,
#                 "position": user.instructor.position,
#                 "degree": user.instructor.degree,
#                 "joined_year": user.instructor.joined_year
#             }
        
#         return {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "phone": user.phone,
#             "created_at": user.created_at.isoformat() if user.created_at else None,
#             "user_type": user_type,
#             "detail": user_detail,
#             "roles": roles,
#             "permissions": permissions
#         }