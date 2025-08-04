from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'dev-secret-key-not-for-production'

# Enable debug mode with verbose error reporting
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

def init_db():
    """Initialize the database with sample products"""
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            category TEXT,
            stock INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            product_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Insert sample products
    products = [
        ('Premium Laptop', 1299.99, 'High-performance laptop for professionals', 'Electronics', 15),
        ('Wireless Headphones', 199.99, 'Noise-cancelling bluetooth headphones', 'Electronics', 25),
        ('Office Chair', 349.99, 'Ergonomic office chair with lumbar support', 'Furniture', 8),
        ('Gaming Monitor', 449.99, '27-inch 4K gaming monitor', 'Electronics', 12),
        ('Desk Lamp', 89.99, 'LED desk lamp with adjustable brightness', 'Furniture', 20)
    ]
    
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO products (name, price, description, category, stock) VALUES (?, ?, ?, ?, ?)', products)
    
    conn.commit()
    conn.close()

def get_products():
    """Get all products from database"""
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

@app.route('/')
def home():
    """Homepage with company information"""
    return render_template('home.html')

@app.route('/products')
def products():
    """Products catalog page"""
    products_list = get_products()
    return render_template('products.html', products=products_list)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with potential vulnerability"""
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    
    # Vulnerable query that can cause errors exposing Flask version
    try:
        # This will cause detailed error messages if product_id is manipulated
        cursor.execute(f'SELECT * FROM products WHERE id = {product_id}')
        product = cursor.fetchone()
        conn.close()
        
        if not product:
            # Force an error that will show Flask debug information
            raise ValueError(f"Product with ID {product_id} not found in catalog")
        
        return render_template('product_detail.html', product=product)
        
    except Exception as e:
        # Re-raise to trigger Flask's debug error handler
        raise e

@app.route('/order', methods=['POST'])
def place_order():
    """Place an order - vulnerable endpoint"""
    customer_name = request.form.get('customer_name')
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')
    
    # Vulnerable parameter handling that can trigger errors
    try:
        # This will cause detailed Flask errors if parameters are malformed
        product_id = int(product_id)
        quantity = int(quantity)
        
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        
        # Get product details
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        
        if not product:
            # Force detailed error with Flask version info
            raise RuntimeError(f"Invalid product ID: {product_id}. Database integrity check failed.")
        
        total_price = product[2] * quantity  # price * quantity
        
        cursor.execute('INSERT INTO orders (customer_name, product_id, quantity, total_price) VALUES (?, ?, ?, ?)',
                      (customer_name, product_id, quantity, total_price))
        
        conn.commit()
        conn.close()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('products'))
        
    except ValueError as e:
        # This will expose Flask version in debug mode
        raise ValueError(f"Invalid order parameters provided: {e}")
    except Exception as e:
        # Re-raise to show full Flask debug information
        raise e

@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler that can expose debug info"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 handler - will show debug info in debug mode"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    # Run with debug mode enabled to show detailed error messages including Flask version
    app.run(debug=True, host='0.0.0.0', port=3206) 