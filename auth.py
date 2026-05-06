from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, Role, ActivityLog
from database import db
import uuid, datetime

def init_auth_routes(app):
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify({'error': 'بيانات الدخول غير صحيحة'}), 401
        role = Role.query.get(user.role_id)
        perms = role.get_perms() if role else []
        access_token = create_access_token(identity=user.id)
        log = ActivityLog(
            id=str(uuid.uuid4()),
            user_id=user.id,
            user_name=user.fullname or user.username,
            action='تسجيل دخول',
            target='نظام',
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'fullname': user.fullname,
                'role': role.name if role else '',
                'perms': perms
            }
        })

    @app.route('/api/me', methods=['GET'])
    @jwt_required()
    def me():
        uid = get_jwt_identity()
        user = User.query.get(uid)
        if not user:
            return jsonify({'error': 'غير موجود'}), 404
        role = Role.query.get(user.role_id)
        return jsonify({
            'id': user.id,
            'username': user.username,
            'fullname': user.fullname,
            'role': role.name if role else '',
            'perms': role.get_perms() if role else []
        })