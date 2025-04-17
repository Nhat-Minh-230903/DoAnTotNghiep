# role_api.py
from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Users, Student, Instructor, UserRole, Role, Faculty, Major,Permission
from BE.app.controllers.api.admin import role_required

role_bp = Blueprint('role_bp', __name__)

# GET /roles - Lấy danh sách roles
@role_bp.route('/roles', methods=['GET'])
@role_required(['Admin'])
def get_roles():
    roles = Role.query.all()
    data = [{'id': r.id, 'name': r.name, 'description': r.description} for r in roles]
    return jsonify(data), 200

# GET /roles/<role_id> - Chi tiết 1 role
@role_bp.route('/roles/<int:role_id>', methods=['GET'])
@role_required(['admin'])
def get_role(role_id):
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role không tồn tại'}), 404
    return jsonify({
        'id': role.id,
        'name': role.name,
        'description': role.description
    }), 200

# POST /roles - Tạo mới role
@role_bp.route('/roles', methods=['POST'])
@role_required(['admin'])
def create_role():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if Role.query.filter_by(name=name).first():
        return jsonify({'error': 'Role đã tồn tại'}), 400

    new_role = Role(name=name, description=description)
    db.session.add(new_role)
    db.session.commit()
    return jsonify({'message': 'Tạo role thành công'}), 201

# PUT /roles/<role_id> - Cập nhật role
@role_bp.route('/roles/<int:role_id>', methods=['PUT'])
@role_required(['admin'])
def update_role(role_id):
    data = request.get_json()
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role không tồn tại'}), 404

    role.name = data.get('name', role.name)
    role.description = data.get('description', role.description)
    db.session.commit()
    return jsonify({'message': 'Cập nhật role thành công'}), 200

# DELETE /roles/<role_id> - Xoá role
@role_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_role(role_id):
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role không tồn tại'}), 404
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': 'Xoá role thành công'}), 200

# GET /roles/<role_id>/permissions - Lấy permission của 1 role
@role_bp.route('/roles/<int:role_id>/permissions', methods=['GET'])
@role_required(['admin'])
def get_role_permissions(role_id):
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role không tồn tại'}), 404

    permissions = [{'id': p.id, 'name': p.name, 'code': p.code, 'description': p.description} for p in role.permissions]
    return jsonify({
        'role_id': role.id,
        'role_name': role.name,
        'permissions': permissions
    }), 200

# POST /roles/<role_id>/permissions - Gán permission cho role
@role_bp.route('/roles/<int:role_id>/permissions', methods=['POST'])
@role_required(['admin'])
def add_permission_to_role(role_id):
    data = request.get_json()
    permission_id = data.get('permission_id')

    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role không tồn tại'}), 404

    permission = Permission.query.get(permission_id)
    if not permission:
        return jsonify({'error': 'Permission không tồn tại'}), 404

    if permission in role.permissions:
        return jsonify({'message': 'Role đã có permission này'}), 200

    role.permissions.append(permission)
    db.session.commit()
    return jsonify({'message': 'Gán permission thành công'}), 201

# DELETE /roles/<role_id>/permissions/<permission_id> - Gỡ permission khỏi role
@role_bp.route('/roles/<int:role_id>/permissions/<int:permission_id>', methods=['DELETE'])
@role_required(['admin'])
def remove_permission_from_role(role_id, permission_id):
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role không tồn tại'}), 404

    permission = Permission.query.get(permission_id)
    if not permission:
        return jsonify({'error': 'Permission không tồn tại'}), 404

    if permission not in role.permissions:
        return jsonify({'message': 'Role không có permission này'}), 200

    role.permissions.remove(permission)
    db.session.commit()
    return jsonify({'message': 'Gỡ permission thành công'}), 200
