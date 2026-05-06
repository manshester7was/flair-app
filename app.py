from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from database import db, init_db
from models import User, Role, Category, Product, Purchase, Sale, ActivityLog, Setting
from auth import init_auth_routes
import uuid, datetime, json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flair_super_secret_key_change_me'
CORS(app)
jwt = JWTManager(app)
init_db(app)

# ========== Helper Functions ==========
def add_log(user_id, user_name, action, target, detail=''):
    log = ActivityLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        user_name=user_name,
        action=action,
        target=target,
        detail=detail,
        timestamp=datetime.datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

def has_perm(uid, perm):
    u = User.query.get(uid)
    if not u: return False
    r = Role.query.get(u.role_id)
    perms = r.get_perms() if r else []
    return perm in perms

# ========== Products API ==========
@app.route('/api/products', methods=['GET'])
@jwt_required()
def get_products():
    uid = get_jwt_identity()
    if not has_perm(uid, 'view_inv'):
        return jsonify({'error': 'لا صلاحية'}), 403
    products = Product.query.all()
    return jsonify([{
        'id': p.id, 'code': p.code, 'name': p.name, 'categoryId': p.category_id,
        'size': p.size, 'costPrice': p.cost_price, 'sellPrice': p.sell_price,
        'status': p.status, 'batchId': p.batch_id, 'notes': p.notes, 'image': p.image
    } for p in products])

@app.route('/api/products', methods=['POST'])
@jwt_required()
def add_product():
    uid = get_jwt_identity()
    if not has_perm(uid, 'add_prod'):
        return jsonify({'error': 'لا صلاحية'}), 403
    data = request.get_json()
    pid = str(uuid.uuid4())
    prod = Product(
        id=pid, code=data['code'], name=data['name'], category_id=data.get('categoryId'),
        size=data.get('size'), cost_price=data.get('costPrice', 0),
        sell_price=data.get('sellPrice', 0), status=data.get('status', 'available'),
        batch_id=data.get('batchId'), notes=data.get('notes'), image=data.get('image')
    )
    db.session.add(prod)
    u = User.query.get(uid)
    add_log(uid, u.fullname or u.username, 'إضافة منتج', data['code'], data['name'])
    db.session.commit()
    return jsonify({'id': pid})

@app.route('/api/products/<pid>', methods=['PUT'])
@jwt_required()
def update_product(pid):
    uid = get_jwt_identity()
    if not has_perm(uid, 'edit_prod'):
        return jsonify({'error': 'لا صلاحية'}), 403
    p = Product.query.get(pid)
    if not p:
        return jsonify({'error': 'غير موجود'}), 404
    data = request.get_json()
    for key, val in data.items():
        if key == 'costPrice':
            p.cost_price = val
        elif key == 'sellPrice':
            p.sell_price = val
        elif key == 'status':
            p.status = val
        elif key == 'name':
            p.name = val
        elif key == 'code':
            p.code = val
        elif key == 'size':
            p.size = val
        elif key == 'notes':
            p.notes = val
        elif key == 'image':
            p.image = val
    u = User.query.get(uid)
    add_log(uid, u.fullname or u.username, 'تعديل منتج', p.code, p.name)
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/products/<pid>', methods=['DELETE'])
@jwt_required()
def delete_product(pid):
    uid = get_jwt_identity()
    if not has_perm(uid, 'del_prod'):
        return jsonify({'error': 'لا صلاحية'}), 403
    p = Product.query.get(pid)
    if p:
        db.session.delete(p)
        u = User.query.get(uid)
        add_log(uid, u.fullname or u.username, 'حذف منتج', p.code, p.name)
        db.session.commit()
    return jsonify({'ok': True})

# ... (بقية APIs: purchases, sales, categories, users, roles, reports, settings)
# هكتبها كاملة في الملف النهائي

if __name__ == '__main__':
    with app.app_context():
        # إنشاء مستخدم Admin أولي
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(id='r1', name='Admin', perms=json.dumps([
                'view_inv','add_prod','edit_prod','del_prod','manage_pur',
                'rec_sale','edit_sale','del_sale','view_rep','manage_users','settings'
            ]))
            db.session.add(admin_role)
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(id='u1', username='admin', password='admin123', fullname='مدير النظام', role_id='r1')
            db.session.add(admin)
        db.session.commit()
    app.run(debug=True, port=5000)