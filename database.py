# database.py
import sqlite3
from datetime import datetime

DB_NAME = "zackie_pharma.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    c = conn.cursor()

    # Users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'staff'
    )
    ''')

    # Categories table
    c.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # Products table
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')

    # Customers / Patients table
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

    # Suppliers table
    c.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        address TEXT
    )
    ''')

    # Inventory / Stock movements table
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        batch_no TEXT,
        quantity_in INTEGER DEFAULT 0,
        quantity_out INTEGER DEFAULT 0,
        expiry_date TEXT,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')

    # Sales / Transactions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        total_amount REAL NOT NULL,
        payment_method TEXT,
        discount REAL DEFAULT 0,
        tax REAL DEFAULT 0,
        sale_date TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')

    # Sales details (link products to sales)
    c.execute('''
    CREATE TABLE IF NOT EXISTS sales_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')

    # Prescriptions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        doctor_name TEXT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        date_prescribed TEXT NOT NULL,
        instructions TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')

    # Audit logs table
    c.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        table_name TEXT NOT NULL,
        record_id INTEGER,
        timestamp TEXT NOT NULL
    )
    ''')

    # Notifications / Alerts table
    c.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        recipient_id INTEGER,
        status TEXT DEFAULT 'pending',
        date_created TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

# Helper function ya audit log
def log_action(action, table_name, record_id=None):
    conn = get_db_connection()
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
    INSERT INTO audit_logs (action, table_name, record_id, timestamp)
    VALUES (?, ?, ?, ?)
    ''', (action, table_name, record_id, timestamp))
    conn.commit()
    conn.close()
