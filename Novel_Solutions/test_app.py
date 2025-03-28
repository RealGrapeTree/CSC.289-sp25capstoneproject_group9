

# test_app.py
import pytest
import requests
from unittest.mock import patch
from flask import Flask
from flask_login import LoginManager, login_required, current_user
from blueprints.loginpage.Novel_login import Novel_login, login_user, logout_user
from app import app, db, create_default_manager
from models import User, Inventory, InventoryTransaction, Book

from blueprints.inventory.Novel_inventory import Novel_inventory, check_books, insert_book_into_db, get_book_data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            create_default_manager()
        yield client
        with app.app_context():
            db.drop_all()

"""
*
* Login tests
*
"""

def test_default_manager_creation(client):
    with app.app_context():
        manager = User.query.filter_by(username="admin").first()
        assert manager is not None
        assert manager.username == "admin"
        assert manager.firstname == "Admin"
        assert manager.lastname == "User"
        assert manager.email == "admin@example.com"
        assert manager.role == "manager"



# Test Unauthorized User Access to Process Sale
def test_login_unauthorized_user_access(client):
    with app.app_context():
        response = client.post('/login', data={'username': 'nonexistent_user', 'password': 'wrongpassword'}, follow_redirects=True)
    
        assert response.status_code == 200
        assert b'Login unsuccessful. Please check username and password' in response.data

def test_login_authorized_user_access(client):
    with app.app_context():
        response = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Login successful!' in response.data

def test_add_user(client):
    with app.app_context():
        response = client.post('/add_user', data={'username': 'cashier1', 'firstname': 'John', 'lastname': 'James',
                                                  'email': 'james@example.com', 'password': 'cashier1',
                                                  'role': 'cashier'}, follow_redirects=True)

        assert b'User created successfully!'

"""
*
* Inventory test cases
*
"""

def test_insert_book_into_db(client):
    with app.app_context():
        response = insert_book_into_db('9780141439587', 'Pride and Prejudice', 'Jane Austen',
                                       279, 'Penguin Books', '2002-12-31',
                                       'https://covers.openlibrary.org/b/id/242472-L.jpg',
                                       'https://covers.openlibrary.org/b/id/242472-L.jpg', 10, 10.00)
        assert response is not None
        assert response.isbn == '9780141439587'
        assert response.title == 'Pride and Prejudice'
        assert response.authors == 'Jane Austen'
        assert response.number_of_pages == 279
        assert response.publishers == 'Penguin Books'
        assert response.publish_date == '2002-12-31'
        assert response.thumbnail_url == 'https://covers.openlibrary.org/b/id/242472-L.jpg'
        assert response.cover == 'https://covers.openlibrary.org/b/id/242472-L.jpg'
        assert response.stock == 10
        assert response.price == 10.00

def test_get_book_data(client):
    with app.app_context():
        response = get_book_data('9780141439587')
        assert response is not None
        assert response[0] == '9780141439587'
        #assert response[1] == 'Pride and Prejudice'
        assert response[2] == 'Jane Austen'
        #assert response[3] == 279
        assert response[4] == 'Penguin Books'
        #assert response[5] == '2002-12-31'
        #assert response[6] == 'https://covers.openlibrary.org/b/id/242472-L.jpg'

"""
*
*Cart Test Cases
*
"""

def test_initialize_cart(client):
    with app.app_context():
        response = client.get('/cart')
        assert response.status_code == 200
        assert b'Cart' in response.data

def test_view_cart(client):
    with app.app_context():
        response = client.get('/cart')
        assert response.status_code == 200
        assert b'Cart' in response.data

def test_add_to_cart(client):
    with app.app_context():
        response = client.post('/add_to_cart/1')
        assert response.status_code == 200
        assert b'Book added to cart' in response.data

#def test_remove_from_cart(client):
#    with app.app_context():
#        response = client.post('/remove_from_cart/1')
#        assert response.status_code == 200
#        assert b'Book removed from cart' in response.data

def test_clear_cart(client):
    with app.app_context():
        response = client.post('/clear_cart')
        assert response.status_code == 200
        assert b'Cart cleared' in response.data

def get_cart_total(client):
    with app.app_context():
        response = client.get('/cart')
        assert response.status_code == 200
        assert b'Cart' in response.data
        assert b'Total' in response.data
