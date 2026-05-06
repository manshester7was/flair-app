from database import db
from datetime import datetime
import json

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    fullname = db.Column(db.String(120))
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    perms = db.Column(db.Text)  # JSON string

    def get_perms(self):
        return json.loads(self.perms) if self.perms else []

    def set_perms(self, perms_list):
        self.perms = json.dumps(perms_list)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    prefix = db.Column(db.String(10), nullable=False, unique=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.String(36), primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'))
    size = db.Column(db.String(50))
    cost_price = db.Column(db.Float, default=0)
    sell_price = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='available')  # available, reserved, sold
    batch_id = db.Column(db.String(36), db.ForeignKey('purchases.id'))
    notes = db.Column(db.Text)
    image = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    total_cost = db.Column(db.Float, default=0)
    item_count = db.Column(db.Integer, default=0)
    cost_per_item = db.Column(db.Float, default=0)
    supplier = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.String(36), primary_key=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'))
    price = db.Column(db.Float, nullable=False)
    customer = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    date = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    profit = db.Column(db.Float, default=0)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    user_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    user_name = db.Column(db.String(120))
    action = db.Column(db.String(200))
    target = db.Column(db.String(200))
    detail = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Setting(db.Model):
    __tablename__ = 'settings'
    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.Text)