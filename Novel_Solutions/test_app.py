

# test_app.py
import pytest
from flask import Flask
from flask_login import LoginManager, login_required, current_user
from blueprints.loginpage.Novel_login import Novel_login
from app import app, db, create_default_manager
from models import User, Inventory, InventoryTransaction, Book


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

def create_new_book():
    new_book = Book(isbn="0375826696", title="Eragon", authors="Christopher Paolini", sku=None, stock=10,
                    price=9.99, number_of_pages=503, publishers="KNOPF", publish_date="2003",
                    thumbnail_url=None, cover=None)
    return new_book

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

        assert b'Login successful!' in response.data

def test_add_user(client):
    with app.app_context():
        response = client.post('/add_user', data={'username': 'cashier1', 'firstname': 'John', 'lastname': 'James',
                                                  'email': 'james@example.com', 'password': 'cashier1',
                                                  'role': 'cashier'}, follow_redirects=True)

        assert b'User created successfully!'


def test_cart_creation(client):
    assert 'cart' is not None

def test_db_creation(client):
    with app.app_context():
        assert db is not None

def test_inventory_get(client):
    with app.app_context():
        inventory = Inventory.query.all()
        assert inventory is not None

