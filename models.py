# models.py
from database import db
from flask_login import UserMixin
from datetime import datetime

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    
    # Liên kết với bảng Table, mỗi venue có thể có nhiều bàn
    tables = db.relationship('Table', backref='venue', lazy=True)
    menu_items = db.relationship('MenuItem', backref='venue', lazy=True)  # Liên kết với MenuItem

    # Tham chiếu đến User (mỗi venue thuộc về một user)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Table(db.Model):
    __tablename__ = 'tables'  # Đổi tên bảng từ 'table' thành 'tables'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)


class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Tên món ăn
    price = db.Column(db.Float, nullable=False)  # Giá món ăn
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)  # Tham chiếu tới nhà hàng

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_owner = db.Column(db.Boolean, default=False)  # Thêm cột is_owner để phân biệt chủ nhà hàng

    # Liên kết với bảng Venue, mỗi user có thể sở hữu nhiều venue
    venues = db.relationship('Venue', backref='user', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Quan hệ với Order và MenuItem (nếu có)
    order = db.relationship('Order', backref=db.backref('order_items', lazy=True))
    menu_item = db.relationship('MenuItem', backref=db.backref('order_items', lazy=True))


# Chức năng tạo người dùng, sử dụng bcrypt từ app.py
def create_user(username, password, bcrypt):
    """Hàm tạo người dùng với mật khẩu đã mã hóa"""
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

