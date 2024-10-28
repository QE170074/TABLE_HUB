from flask import Flask, render_template, redirect, request, url_for, flash, session  # Import flash để sử dụng thông báo
from config import Config
from database import db
from models import Venue, Table, User, MenuItem, Order, OrderItem 
from werkzeug.security import generate_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime

# Khởi tạo Flask app và các công cụ
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'  # Cần thiết để sử dụng flash

# Khởi tạo các đối tượng cần thiết
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Khởi tạo Flask-Migrate
migrate = Migrate(app, db)  

# Khởi tạo cơ sở dữ liệu và bảng nếu chưa tồn tại
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return render_template('home.html')  # Gọi đúng file template


# Route bảng điều khiển
@app.route('/dashboard')
@login_required
def dashboard():
    """Trang bảng điều khiển sau khi đăng nhập"""
    if current_user.is_owner:
        return render_template('dashboard.html')
    else:
        return render_template('customer_home.html')


# Route đăng ký người dùng
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_owner = 'is_owner' in request.form  # Kiểm tra nếu đây là chủ nhà hàng
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Tên đăng nhập đã tồn tại, vui lòng chọn tên khác.", 'error')
            return render_template('register.html')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(username=username, password=hashed_password, is_owner=is_owner)
        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công! Vui lòng đăng nhập.", 'success')
        return redirect('/login')
    
    return render_template('register.html')


# Route đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Đăng nhập thành công!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng.", 'error')

    return render_template('login.html')


# Route đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất thành công.", 'success')
    return redirect(url_for('login'))


# Route quản lý danh sách bàn
@app.route('/manage_tables')
@login_required
def manage_tables():
    if not current_user.is_owner:
        return redirect(url_for('home'))
    
    venues = Venue.query.filter_by(user_id=current_user.id).all()
    return render_template('manage_table.html', venues=venues)


# Cập nhật trạng thái bàn
@app.route('/admin/edit/<int:table_id>', methods=['GET', 'POST'])
@login_required
def edit_table(table_id):
    table = db.session.get(Table, table_id)
    
    if request.method == 'POST':
        status = request.form.get('status')
        table.is_available = status == 'available'
        db.session.commit()
        flash("Cập nhật trạng thái bàn thành công.", 'success')
        return redirect(url_for('manage_tables'))

    return render_template('edit_table.html', table=table)


# Route quản lý nhà hàng
@app.route('/manage_restaurants')
@login_required
def manage_restaurants():
    if not current_user.is_owner:
        return redirect(url_for('home'))
    
    venues = Venue.query.filter_by(user_id=current_user.id).all()
    return render_template('manage_venue.Fhtml', venues=venues)


# Route thêm bàn (Table)
@app.route('/add_table/<int:venue_id>', methods=['GET', 'POST'])
@login_required
def add_table(venue_id):
    venue = db.session.get(Venue, venue_id)
    
    if request.method == 'POST':
        number = request.form['number']
        new_table = Table(number=number, venue_id=venue.id)
        db.session.add(new_table)
        db.session.commit()
        flash("Thêm bàn thành công.", 'success')
        return redirect(url_for('manage_tables'))
    
    return render_template('add_table.html', venue=venue)


# Route thêm món ăn (MenuItem)
@app.route('/add_menu_item/<int:venue_id>', methods=['GET', 'POST'])
@login_required
def add_menu_item(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        if not name or not price:
            flash("Vui lòng nhập đầy đủ thông tin món ăn.", 'error')
            return redirect(url_for('add_menu_item', venue_id=venue.id))
        
        try:
            new_menu_item = MenuItem(name=name, price=float(price), venue_id=venue.id)
            db.session.add(new_menu_item)
            db.session.commit()
            flash("Thêm món ăn thành công.", 'success')
            return redirect(url_for('manage_menu', venue_id=venue.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi: {e}", 'error')
            return redirect(url_for('add_menu_item', venue_id=venue.id))
    
    return render_template('add_menu_item.html', venue=venue)


# Route chỉnh sửa món ăn (MenuItem)
@app.route('/edit_menu_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)
    
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        db.session.commit()
        flash("Cập nhật món ăn thành công.", "success")
        return redirect(url_for('manage_menu', venue_id=item.venue_id))

    return render_template('edit_menu_item.html', item=item)


# Route quản lý món ăn
@app.route('/manage_menu')
@login_required
def manage_menu():
    if not current_user.is_owner:
        return redirect(url_for('home'))
    
    venues = Venue.query.filter_by(user_id=current_user.id).all()
    return render_template('manage_menu.html', venues=venues)


# Route xem đơn hàng
@app.route('/owner/orders')
@login_required
def view_orders():
    if not current_user.is_owner:
        flash("Bạn không có quyền truy cập trang này.", "error")
        return redirect(url_for('home'))
    
    venues = Venue.query.filter_by(user_id=current_user.id).all()
    venue_ids = [venue.id for venue in venues]
    orders = Order.query.filter(Order.venue_id.in_(venue_ids)).all()
    
    return render_template('view_orders.html', orders=orders)









                                                      #ROUTE FOR CUSTOMER
# Trang chủ khách hàng
@app.route('/customer_home')
def customer_home():
    return render_template('customer_home.html')


# Xem danh sách nhà hàng
@app.route('/venues', methods=['GET'])
def view_venues():
    venues = Venue.query.all()
    return render_template('view_venues.html', venues=venues)


# Xem danh sách bàn của nhà hàng
@app.route('/tables/<int:venue_id>', methods=['GET'])
def view_tables(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    return render_template('view_tables.html', venue=venue)


# Đặt bàn
@app.route('/book_table/<int:table_id>', methods=['GET', 'POST'])
@login_required
def book_table(table_id):
    table = Table.query.get_or_404(table_id)
    if table.is_available:
        table.is_available = False
        db.session.commit()
        flash(f"Đặt bàn số {table.number} tại {table.venue.name} thành công!", 'success')
    else:
        flash("Bàn đã được đặt.", "error")
    return redirect(url_for('view_tables', venue_id=table.venue.id))


# Xem menu của nhà hàng
@app.route('/view_menu/<int:venue_id>', methods=['GET'])
def view_menu(venue_id):
    venue = db.session.get(Venue, venue_id)
    if venue:
        menu_items = MenuItem.query.filter_by(venue_id=venue_id).all()
        session['venue_id'] = venue_id
        return render_template('view_menu.html', venue=venue, menu_items=menu_items)
    else:
        flash("Không tìm thấy nhà hàng.", 'error')
        return redirect(url_for('view_venues'))


# Thêm món vào giỏ hàng
@app.route('/order_item/<int:item_id>', methods=['POST'])
@login_required
def order_item(item_id):
    """Thêm món vào giỏ hàng."""
    item = MenuItem.query.get_or_404(item_id)

    # Kiểm tra nếu venue_id có trong session chưa
    venue_id = session.get('venue_id')
    if not venue_id:
        flash("Không tìm thấy nhà hàng.", 'error')
        return redirect(url_for('view_venues'))

    # Lấy danh sách các món đã đặt trong session
    ordered_items = session.get('ordered_items', [])
    ordered_items.append({'id': item.id, 'name': item.name, 'price': item.price})
    session['ordered_items'] = ordered_items  # Lưu lại vào session

    flash(f"Bạn đã thêm {item.name} vào giỏ hàng.", 'success')
    return redirect(url_for('view_menu', venue_id=venue_id))  # Điều hướng về menu để tiếp tục chọn món

# Xác nhận đơn hàng
@app.route('/confirm_order', methods=['POST', 'GET'])
@login_required
def confirm_order():
    ordered_items = session.get('ordered_items', [])
    if not ordered_items:
        flash("Giỏ hàng của bạn trống.", "warning")
        return redirect(url_for('view_menu', venue_id=session.get('venue_id')))
    
    # Tính tổng tiền của đơn hàng
    total_price = sum(item['price'] for item in ordered_items)

    # Xử lý đơn hàng: lưu vào cơ sở dữ liệu hoặc các hành động cần thiết khác
    # Ví dụ, tạo một đơn hàng mới với giá trị tổng tiền và trạng thái mặc định là 'pending':
    order = Order(
        customer_id=current_user.id, 
        venue_id=session.get('venue_id'), 
        total_price=total_price,  # Gán tổng tiền
        status='pending',  # Gán trạng thái mặc định
        created_at=datetime.utcnow()  # Nếu mô hình yêu cầu giá trị thời gian
    )
    db.session.add(order)
    db.session.commit()

    # Thêm các mục từ giỏ hàng vào đơn hàng
    for item in ordered_items:
        order_item = OrderItem(order_id=order.id, menu_item_id=item['id'], price=item['price'])
        db.session.add(order_item)
    
    # Xóa giỏ hàng sau khi xác nhận
    session.pop('ordered_items', None)
    db.session.commit()

    flash("Đơn hàng của bạn đã được xác nhận!", 'success')
    return redirect(url_for('view_venues'))  # Điều hướng người dùng về trang danh sách nhà hàng hoặc nơi khác



# Xem giỏ hàng
@app.route('/view_cart', methods=['GET'])
@login_required
def view_cart():
    ordered_items = session.get('ordered_items', [])
    if not ordered_items:
        flash("Giỏ hàng của bạn trống.", "warning")
        return redirect(url_for('view_menu', venue_id=session.get('venue_id')))
    
    total_price = sum(item['price'] for item in ordered_items)
    return render_template('view_cart.html', ordered_items=ordered_items, total_price=total_price)


# Xóa món khỏi giỏ hàng
@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    ordered_items = session.get('ordered_items', [])
    
    # Xóa món có id là item_id khỏi giỏ hàng
    ordered_items = [item for item in ordered_items if item['id'] != item_id]
    session['ordered_items'] = ordered_items  # Cập nhật lại giỏ hàng trong session

    flash("Món đã được xóa khỏi giỏ hàng.", 'success')
    return redirect(url_for('view_cart'))


# Route thanh toán (Checkout)
@app.route('/checkout', methods=['GET'])
@login_required
def checkout():
    ordered_items = session.get('ordered_items', [])
    if not ordered_items:
        flash("Giỏ hàng của bạn trống.", "warning")
        return redirect(url_for('view_menu', venue_id=session.get('venue_id')))
    
    total_price = sum(item['price'] for item in ordered_items)

    # Đường dẫn đến hình ảnh mã QR (Techcombank trong ví dụ của bạn)
    qr_code_url = "/static/techcom.png"

    return render_template('qr_payment.html', ordered_items=ordered_items, total_price=total_price, qr_code_url=qr_code_url)


if __name__ == '__main__':
    app.run(debug=True)





