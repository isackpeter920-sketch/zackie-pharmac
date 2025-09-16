from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Badilisha hii kwa secret yako

# --- Login Required Decorator ---
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Tafadhali ingia kwanza.")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# --- Add Product Route ---
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']

        if not name or not price or not quantity:
            flash("Tafadhali jaza field zote!")
            return redirect(url_for('add_product'))

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            flash("Tafadhali ingiza namba sahihi kwa price na quantity!")
            return redirect(url_for('add_product'))

        conn = sqlite3.connect('zackie_pharma.db')
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                  (name, price, quantity))
        conn.commit()
        conn.close()

        flash("Product imeongezwa kwa mafanikio!")
        return redirect(url_for('dashboard'))  # Redirect baada ya success

    return render_template('add_product.html')


# --- Sample dashboard route (badilisha kama unayo dashboard yako) ---
@app.route('/dashboard')
@login_required
def dashboard():
    return "Welcome to Dashboard!"

# --- Sample login route (kwa testing) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user_id'] = 1
        flash("Umeingia!")
        return redirect(url_for('dashboard'))
    return '''
        <form method="POST">
            <input type="submit" value="Login">
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
