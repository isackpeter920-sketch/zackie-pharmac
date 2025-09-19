import sqlite3
from datetime import datetime

DB_NAME = "zackie_pharma.db"

# ====== Database Connection ======
def get_db_connection():
    return sqlite3.connect(DB_NAME)

# ====== Create Tables ======
def create_tables():
    conn = get_db_connection()
    c = conn.cursor()

    # Users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'cashier'
    )
    ''')

    # Products table
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )
    ''')

    # Customers table
    c.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        dob TEXT,
        medical_history TEXT
    )
    ''')

    # Sales table
    c.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        discount REAL DEFAULT 0,
        tax REAL DEFAULT 0,
        sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    ''')

    # Sales details table
    c.execute('''
    CREATE TABLE IF NOT EXISTS sales_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY(sale_id) REFERENCES sales(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    ''')

    # Prescriptions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        doctor_name TEXT,
        product_id INTEGER,
        quantity INTEGER,
        date_prescribed TEXT,
        instructions TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    ''')

    conn.commit()
    conn.close()

# ====== CRUD Functions ======
def add_product(name, category_id, price, quantity):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
    INSERT INTO products (name, category_id, price, quantity)
    VALUES (?, ?, ?, ?)
    ''', (name, category_id, price, quantity))
    conn.commit()
    product_id = c.lastrowid
    conn.close()
    return product_id


def add_customer(name, phone=None, email=None, address=None, dob=None, medical_history=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
    INSERT INTO customers (name, phone, email, address, dob, medical_history)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, phone, email, address, dob, medical_history))
    conn.commit()
    customer_id = c.lastrowid
    conn.close()
    return customer_id


def add_sale(customer_id, total_amount, payment_method, discount=0, tax=0, sale_date=None, products=[]):
    if not sale_date:
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
    INSERT INTO sales (customer_id, total_amount, payment_method, discount, tax, sale_date)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (customer_id, total_amount, payment_method, discount, tax, sale_date))
    sale_id = c.lastrowid

    # Insert sales details
    for p in products:
        c.execute('''
        INSERT INTO sales_details (sale_id, product_id, quantity, price)
        VALUES (?, ?, ?, ?)
        ''', (sale_id, p['product_id'], p['quantity'], p['price']))
    conn.commit()
    conn.close()
    return sale_id


def add_prescription(customer_id, doctor_name, product_id, quantity, date_prescribed=None, instructions=None):
    if not date_prescribed:
        date_prescribed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
    INSERT INTO prescriptions (customer_id, doctor_name, product_id, quantity, date_prescribed, instructions)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (customer_id, doctor_name, product_id, quantity, date_prescribed, instructions))
    conn.commit()
    prescription_id = c.lastrowid
    conn.close()
    return prescription_id


if __name__ == "__main__":
    create_tables()
    print("✅ Database setup complete! Tables and CRUD functions ready.")
