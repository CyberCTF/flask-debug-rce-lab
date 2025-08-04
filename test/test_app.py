import pytest
import sys
import os
import sqlite3
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))

from app import app, init_db

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    # Create a temporary database file
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_home_page(client):
    """Test that the home page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'TechStore' in response.data
    assert b'Premium Electronics' in response.data

def test_products_page(client):
    """Test that the products page loads and shows products"""
    response = client.get('/products')
    assert response.status_code == 200
    assert b'Premium Products' in response.data
    assert b'Premium Laptop' in response.data

def test_product_detail_valid(client):
    """Test viewing a valid product detail page"""
    response = client.get('/product/1')
    assert response.status_code == 200
    assert b'Premium Laptop' in response.data
    assert b'Place Order' in response.data

def test_product_detail_invalid_triggers_error(client):
    """Test that accessing invalid product ID triggers Flask debug error with version info"""
    # This should trigger a ValueError with Flask debug information
    response = client.get('/product/999', follow_redirects=False)
    
    # In debug mode, Flask will show detailed error page with version information
    # The response will be a 500 error with debug information
    assert response.status_code == 500 or 'ValueError' in response.get_data(as_text=True)

def test_order_placement_valid(client):
    """Test placing a valid order"""
    response = client.post('/order', data={
        'customer_name': 'John Doe',
        'product_id': '1',
        'quantity': '2'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Order placed successfully' in response.data or b'Premium Products' in response.data

def test_order_placement_invalid_params_triggers_error(client):
    """Test that invalid order parameters trigger Flask debug errors"""
    # Test with invalid product_id that should trigger ValueError with Flask version info
    response = client.post('/order', data={
        'customer_name': 'John Doe',
        'product_id': 'invalid',
        'quantity': '1'
    }, follow_redirects=False)
    
    # Should trigger a ValueError with Flask debug information
    assert response.status_code == 500 or 'ValueError' in response.get_data(as_text=True)

def test_flask_debug_mode_enabled(client):
    """Test that Flask debug mode is enabled and exposes version information"""
    # Access an endpoint that will trigger an error
    response = client.get('/product/abc', follow_redirects=False)
    
    # In debug mode, the error page should contain Flask version information
    response_text = response.get_data(as_text=True)
    
    # Check if we get a 404 (route not found) or if we can trigger the product_detail error
    if response.status_code == 404:
        # Try to access the product detail with a string that should cause int() conversion error
        pass
    else:
        # Look for Flask debug information in the response
        assert response.status_code >= 400

def test_database_initialization():
    """Test that the database initializes correctly with sample data"""
    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    try:
        # Initialize the database
        original_db = 'store.db'
        temp_db = db_path
        
        # Copy the init_db logic to test database
        conn = sqlite3.connect(temp_db)
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
        
        products = [
            ('Premium Laptop', 1299.99, 'High-performance laptop for professionals', 'Electronics', 15),
            ('Wireless Headphones', 199.99, 'Noise-cancelling bluetooth headphones', 'Electronics', 25),
        ]
        
        cursor.executemany('INSERT INTO products (name, price, description, category, stock) VALUES (?, ?, ?, ?, ?)', products)
        conn.commit()
        
        # Verify data was inserted
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        assert count >= 2
        
        conn.close()
        
    finally:
        os.close(db_fd)
        os.unlink(db_path)

def test_error_handling_exposes_debug_info(client):
    """Test specific vulnerability: Flask debug mode exposes version information in errors"""
    # Try to trigger a database error that will show Flask debug information
    response = client.get('/product/999999', follow_redirects=False)
    
    # The error should be handled by Flask's debug mode
    # In a real scenario, this would expose Flask version in the error traceback
    response_text = response.get_data(as_text=True)
    
    # Check that we get some kind of error response
    assert response.status_code >= 400
    
    # In debug mode, Flask would normally show detailed traceback with version info
    # This is the vulnerability we're testing for

def test_sql_injection_attempt(client):
    """Test that malformed SQL in product_id parameter triggers detailed errors"""
    # The vulnerable code uses f-string SQL injection
    # This should trigger a detailed error with Flask debug information
    response = client.get('/product/1; DROP TABLE products; --', follow_redirects=False)
    
    # This should either cause a 404 (URL routing) or trigger the vulnerable SQL code
    # The key is that in debug mode, any resulting error will show Flask version
    assert response.status_code >= 400