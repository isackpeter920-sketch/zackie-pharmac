from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route ya login
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

# Route ya dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route ya add product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    return render_template('add_product.html')

# Route ya sales
@app.route('/sales')
def sales():
    return render_template('sales.html')

# Route ya logout (Step 8a)
@app.route('/logout')
def logout():
    # Baadaye hapa tuta-clear session
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
