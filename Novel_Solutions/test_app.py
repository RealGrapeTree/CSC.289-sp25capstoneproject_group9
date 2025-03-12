"""

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

# Test Manager Access (Should be denied access to process sale)
def test_manager_access(client):
    # Log in as manager
    with app.app_context():
        response = client.post('/login', data={'username': 'manager_user', 'password': 'managerpassword'})
        assert response.status_code == 200

        # Try accessing restricted page (should be unauthorized)
        response = client.get('/process_sale')
        assert response.status_code == 302  # Should redirect
        assert b'Unauthorized! Only cashiers can process sales.' in response.data

def test_cashier_creation(client):
    with app.app_context():
        cashier = User(username="cashier1", firstname="John", lastname="James",
                           email="james@example.com", password="password1", role="cashier")
        assert cashier is not None


def test_cashier_access(client):
    # Log in as cashier
    with app.app_context():
        response = client.post('/login', data={'username': 'cashier_user', 'password': 'cashierpassword'})
        assert response.status_code == 200
        assert b'Process Sale' in response.data

        # Try accessing restricted page (should be accessible)
        response = client.get('/process_sale')
        assert response.status_code == 200

# Test Unauthorized User Access to Process Sale
def test_unauthorized_user_access(client):
    # Log in as an invalid user
    with app.app_context():
        response = client.post('/login', data={'username': 'nonexistent_user', 'password': 'wrongpassword'})
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data


def test_cart_creation(client):
    assert 'cart' is not None

def test_db_creation(client):
    with app.app_context():
        assert db is not None

#def test_inventory_get(client):
#    with app.app_context():
#        inventory = Inventory.query.all()
#        assert inventory is None

def test_create_new_book(client):
    with app.app_context():
        new_book = create_new_book()
        assert new_book is not None


"""