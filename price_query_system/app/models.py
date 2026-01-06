from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')  # admin, staff
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 货号
    barcode = db.Column(db.String(50), index=True)  # 条码
    name = db.Column(db.String(200), nullable=False, index=True)  # 产品名称
    model = db.Column(db.String(100))  # 型号
    specification = db.Column(db.String(200))  # 规格
    unit = db.Column(db.String(20))  # 单位
    retail_price = db.Column(db.Float, default=0)  # 零售价
    wholesale_price = db.Column(db.Float, default=0)  # 批发价
    wholesale_min_qty = db.Column(db.Integer, default=1)  # 批发最小数量
    stock = db.Column(db.Integer, default=0)  # 库存
    description = db.Column(db.Text)  # 产品描述
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # 关系
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.product_code} - {self.name}>'

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)  # 是否为主图
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductImage {self.id}>'

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 订单号
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    customer_address = db.Column(db.Text)
    total_amount = db.Column(db.Float, default=0)  # 总金额
    total_quantity = db.Column(db.Integer, default=0)  # 总数量
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, completed, cancelled
    notes = db.Column(db.Text)  # 备注
    notified = db.Column(db.Boolean, default=False)  # 是否已通知
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 关系
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_no}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200))
    product_code = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0)
    subtotal = db.Column(db.Float, default=0)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSetting {self.key}>'
