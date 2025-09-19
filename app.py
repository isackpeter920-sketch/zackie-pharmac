from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, add_product  # + functions nyingine kama add_customer, add_sale
import functools

app = Flask(__name__)
app.secret_key = "replace_with_a_strong_secret_key"

# ============================
# Login Required Decorator
# ============================
def login_required(role=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash("Tafadhali ingia kwanza.")
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("Unauthorized access!")
                return redirect(url_for('dashboard'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ============================
# Routes - Authentication
# ============================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'cashier')

        if not username or not password:
            flash("Tafadhali jaza field zote!")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, hashed_password, role))
            conn.commit()
            flash("User imejiregister kwa mafanikio!")
            return redirect(url_for('login'))
        except Exception as e:
            flash("Username tayari ipo au kuna error: " + str(e))
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            flash("Umeingia!")
            return redirect(url_for('dashboard'))
        else:
            flash("Username au password si sahihi!")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required()
def logout():
    session.clear()
    flash("Umetoka kwenye account yako.")
    return redirect(url_for('login'))

# ============================
# Routes - Dashboard
# ============================
@app.route('/dashboard')
@login_required()
def dashboard():
    return render_template('dashboard.html')


# ============================
# Routes - Products
# ============================
@app.route('/products', methods=['GET', 'POST'])
@login_required(role='admin')  # only admin can add products
def products():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']

        if not name or not price or not quantity:
            flash("Tafadhali jaza field zote!")
            return redirect(url_for('products'))

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            flash("Tafadhali ingiza namba sahihi!")
            return redirect(url_for('products'))

        add_product(name, None, price, quantity)  # category_id=None for now
        flash("Product imeongezwa kwa mafanikio!")
        return redirect(url_for('products'))

    # Display all products
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products_list = c.fetchall()
    conn.close()
    return render_template('products.html', products=products_list)


# ============================
# Routes - Sales, Customers, Reports etc.
@app.route('/reports', methods=['GET', 'POST'])
@login_required(role='admin')  # only admin can access
def reports():
    conn = get_db_connection()
    c = conn.cursor()

    # Optional: filter by date range
    start_date = request.form.get('start_date') if request.method == 'POST' else None
    end_date = request.form.get('end_date') if request.method == 'POST' else None

    query = "SELECT SUM(total_amount), COUNT(*), SUM(sd.quantity) " \
            "FROM sales s JOIN sales_details sd ON s.id = sd.sale_id"
    params = []
    if start_date and end_date:
        query += " WHERE s.sale_date BETWEEN ? AND ?"
        params = [start_date, end_date]

    c.execute(query, params)
    result = c.fetchone()
    conn.close()

    total_sales = result[0] if result[0] else 0
    total_sales_count = result[1] if result[1] else 0
    total_products_sold = result[2] if result[2] else 0

    return render_template('reports.html',
                           total_sales=total_sales,
                           total_sales_count=total_sales_count,
                           total_products_sold=total_products_sold,
                           start_date=start_date,
                           end_date=end_date)
from database import add_sale, add_customer

@app.route('/sales', methods=['GET', 'POST'])
@login_required(role='cashier')  # Only cashier can record sales
def sales():
    conn = get_db_connection()
    c = conn.cursor()

    # Fetch products
    c.execute("SELECT id, name, price, quantity FROM products")
    products_list = c.fetchall()

    # Fetch customers
    c.execute("SELECT id, name FROM customers")
    customers_list = c.fetchall()
    conn.close()

    if request.method == 'POST':
        customer_id = int(request.form['customer_id'])
        payment_method = request.form['payment_method']
        discount = float(request.form.get('discount', 0))
        tax = float(request.form.get('tax', 0))

        # Collect products sold
        sold_products = []
        for p in products_list:
            qty = int(request.form.get(f'quantity_{p[0]}', 0))
            if qty > 0:
                sold_products.append({
                    'product_id': p[0],
                    'quantity': qty,
                    'price': p[2]
                })

        if not sold_products:
            flash("Tafadhali chagua angalau product moja!")
            return redirect(url_for('sales'))

        total_amount = sum(p['quantity'] * p['price'] for p in sold_products)
        total_amount = total_amount - discount + tax

        add_sale(customer_id, total_amount, payment_method, discount, tax, products=sold_products)
        flash("Sale imefanikiwa kurekodiwa!")
        return redirect(url_for('sales'))

    return render_template('sales.html', products=products_list, customers=customers_list)
# ============================
# Tutayaongeza baada ya products route

# ============================
# Run Flask App
# ============================
if __name__ == "__main__":
    app.run(debug=True)
