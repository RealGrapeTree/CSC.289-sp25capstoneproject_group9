
# Import necessary modules
import pytest


from models import User, Book
from app import app, db, create_default_manager
from blueprints.loginpage.Novel_login import Novel_login, login, load_user, logout, delete_user
import os

from extensions import db, bcrypt, login_manager

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

def test_default_manager_creation(client):
    with app.app_context():
        manager = User.query.filter_by(username="admin").first()
        #
        assert manager is not None

def test_add_user(client):
    with app.app_context():
        new_user = User(username="cashier1", firstname="John", lastname="James",
                           email="james@example.com", password="password1", role="cashier")
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(username="cashier1").first()
        assert user.firstname == "John"

def test_number_of_users_after_add(client):
    with app.app_context():
        new_user = User(username="cashier1", firstname="John", lastname="James",
                        email="james@example.com", password="password1", role="cashier")
        db.session.add(new_user)
        db.session.commit()
        usercount = User.query.count()
        assert usercount == 1

# Test is in need of adjustment

def test_delete_user(client):
    with app.app_context():
        new_user = User(username="cashier1", firstname="John", lastname="James",
                        email="james@example.com", password="password1", role="cashier")
        db.session.add(new_user)
        db.session.delete(new_user)
        db.session.commit()
        assert User.query.count() == 1

def test_search_for_user(client):
    with app.app_context():
        new_user = User(username="cashier1", firstname="John", lastname="James",
                        email="james@example.com", password="password1", role="cashier")
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(username="cashier1").first()
        assert user.username == "nick"

def test_search_for_user_email(client):
    with app.app_context():
        current_user = User.query.filter_by(email="admin@example.com").first()
        assert current_user.email == "admin@example.com"



