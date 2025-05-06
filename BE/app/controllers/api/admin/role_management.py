from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db 
from app.utils.user_helper import role_required  
from app.models.user import Users, Role, UserRole ,Permission, RolePermission

admin_role_bp = Blueprint('admin_role_bp', __name__)
@admin_role_bp.route('/get_user_roles/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_roles(user_id):
    current_user_id = get_jwt_identity()
    current_user_roles = (
        db.session.query(Role.name)
        .join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == current_user_id)
        .all()
    )
    current_user_roles = [r[0] for r in current_user_roles]
    print("Current user ID:", current_user_id)
    print("Current user roles:", current_user_roles)
    print("'Admin' in roles?", 'Admin' in current_user_roles)
    if current_user_id != user_id and 'ADMIN' not in current_user_roles:
        return jsonify({'error': 'Bạn không có quyền xem vai trò của người dùng này'}), 403
                
    user = Users.query.get(user_id)
    if not user or user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc đã bị xoá'}), 404

    roles = (
        db.session.query(Role.id, Role.name)
        .join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == user_id)
        .all()
    )

    role_list = [{'id': r.id, 'name': r.name} for r in roles]

    return jsonify({
        'user_id': user.id,
        'user_name': user.name,
        'roles': role_list
    }), 200
# chỉ định role cho 1 người dùng
@admin_role_bp.route('/assign_role_to_user/<int:user_id>/role/<int:role_id>', methods=['POST'])
@role_required(['Admin'])  # Chỉ admin có quyền gán role
def assign_role_to_user(user_id):
    data = request.get_json()
    role_id = data.get('role_id')

    if not role_id:
        return jsonify({'error': 'Thiếu role_id'}), 400

    # Kiểm tra user tồn tại
    user = Users.query.get(user_id)
    if not user or user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc đã bị xoá'}), 404

    # Kiểm tra role tồn tại
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Vai trò không tồn tại'}), 404

    # Kiểm tra nếu role đã được gán rồi
    existing = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if existing:
        return jsonify({'message': 'Người dùng đã có vai trò này'}), 200

    # Gán role
    new_user_role = UserRole(user_id=user_id, role_id=role_id)
    db.session.add(new_user_role)
    db.session.commit()

    return jsonify({'message': 'Gán vai trò thành công'}), 201

# xóa role  cho 1 người dùng 
@admin_role_bp.route('/remove_role_from_user/<int:user_id>/role/<int:role_id>', methods=['DELETE'])
@role_required(['Admin'])  # Chỉ admin được phép gỡ role
def remove_role_from_user(user_id, role_id):
        # Kiểm tra user tồn tại
    user = Users.query.get(user_id)
    if not user or user.is_deleted:
        return jsonify({'error': 'Người dùng không tồn tại hoặc đã bị xoá'}), 404

    # Kiểm tra role tồn tại
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Vai trò không tồn tại'}), 404

    # Kiểm tra user có role đó không
    user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if not user_role:
        return jsonify({'message': 'Người dùng không có vai trò này'}), 200

    # Xoá role khỏi user
    db.session.delete(user_role)
    db.session.commit()

    return jsonify({'message': 'Gỡ vai trò khỏi người dùng thành công'}), 200

@admin_role_bp.route('', methods=['GET'])
@role_required(['Admin'])
def get_all_roles():
    roles = Role.query.all()
    role_list = [{'id': r.id, 'name': r.name, 'description': r.description} for r in roles]
    return jsonify({'': role_list}), 200

@admin_role_bp.route('', methods=['POST'])
@role_required(['Admin'])
def create_role():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': 'Thiếu tên vai trò'}), 400

    if Role.query.filter_by(name=name).first():
        return jsonify({'error': 'Vai trò đã tồn tại'}), 409

    new_role = Role(name=name, description=description)
    db.session.add(new_role)
    db.session.commit()

    return jsonify({'message': 'Tạo vai trò thành công', 'role_id': new_role.id}), 201


@admin_role_bp.route('/<int:role_id>/permissions', methods=['POST'])
@role_required(['Admin'])
def assign_permission_to_role(role_id):
    data = request.get_json()
    permission_id = data.get('permission_id')

    if not permission_id:
        return jsonify({'error': 'Thiếu permission_id'}), 400

    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Vai trò không tồn tại'}), 404

    permission = Permission.query.get(permission_id)
    if not permission:
        return jsonify({'error': 'Quyền không tồn tại'}), 404

    existing = RolePermission.query.filter_by(role_id=role_id, permission_id=permission_id).first()
    if existing:
        return jsonify({'message': 'Vai trò đã có quyền này'}), 200

    new_rp = RolePermission(role_id=role_id, permission_id=permission_id)
    db.session.add(new_rp)
    db.session.commit()

    return jsonify({'message': 'Gán quyền cho vai trò thành công'}), 201
