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
# ============================
# Tutayaongeza baada ya products route

# ============================
# Run Flask App
# ============================
if __name__ == "__main__":
    app.run(debug=True)
