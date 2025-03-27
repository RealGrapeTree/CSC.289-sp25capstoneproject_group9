

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
def test_inventory_get(client):
    with app.app_context():
        inventory = Inventory.query.all()
        assert inventory is not None

def test_check_books(client):
    with app.app_context():
        # Add some books to the database
        book1 = Book(isbn='1111111111', sku='SKU1', title='Book One', stock=10, price=15.99)
        book2 = Book(isbn='2222222222', sku='SKU2', title='Book Two', stock=5, price=9.99)
        db.session.add(book1)
        db.session.add(book2)
        db.session.commit()

        # Capture the output of the check_books function
        from io import StringIO
        import sys

        captured_output = StringIO()
        sys.stdout = captured_output

        check_books()

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()

        # Check if the output contains the details of the added books
        assert 'ID: 1, ISBN: 1111111111, SKU: SKU1, Title: Book One, Stock: 10, Price: $15.99' in output
        assert 'ID: 2, ISBN: 2222222222, SKU: SKU2, Title: Book Two, Stock: 5, Price: $9.99' in output

def test_insert_book_into_db(client):
    isbn = '1234567890'
    title = 'Test Book'
    authors = 'Author One, Author Two'
    number_of_pages = 300
    publishers = 'Test Publisher'
    publish_date = '2023-01-01'
    thumbnail_url = 'http://example.com/thumbnail.jpg'
    cover = 'http://example.com/cover.jpg'
    stock = 15
    price = 25.99

    new_book = insert_book_into_db(isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover, stock, price)

    book = Book.query.filter_by(isbn=isbn).first()
    assert book is not None
    assert book.title == title
    assert book.authors == authors
    assert book.number_of_pages == number_of_pages
    assert book.publishers == publishers
    assert book.publish_date == publish_date
    assert book.thumbnail_url == thumbnail_url
    assert book.cover == cover
    assert book.stock == stock
    assert book.price == price

def test_insert_book_into_db(client):
    isbn = '1234567890'
    title = 'Test Book'
    authors = 'Author One, Author Two'
    number_of_pages = 300
    publishers = 'Test Publisher'
    publish_date = '2023-01-01'
    thumbnail_url = 'http://example.com/thumbnail.jpg'
    cover = 'http://example.com/cover.jpg'
    stock = 15
    price = 25.99

    new_book = insert_book_into_db(isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover, stock, price)

    book = Book.query.filter_by(isbn=isbn).first()
    assert book is not None
    assert book.title == title
    assert book.authors == authors
    assert book.number_of_pages == number_of_pages
    assert book.publishers == publishers
    assert book.publish_date == publish_date
    assert book.thumbnail_url == thumbnail_url
    assert book.cover == cover
    assert book.stock == stock
    assert book.price == price

def test_get_book_data():
    isbn = '1234567890'
    mock_response = {
        f'ISBN:{isbn}': {
            'title': 'Test Book',
            'authors': [{'name': 'Author One'}, {'name': 'Author Two'}],
            'number_of_pages': 300,
            'publishers': [{'name': 'Test Publisher'}],
            'publish_date': '2023-01-01',
            'cover': {
                'medium': 'http://example.com/thumbnail.jpg',
                'large': 'http://example.com/cover.jpg'
            }
        }
    }

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response

        result = get_book_data(isbn)
        expected = (
            isbn, 'Test Book', 'Author One, Author Two', 300, 'Test Publisher',
            '2023-01-01', 'http://example.com/thumbnail.jpg', 'http://example.com/cover.jpg'
        )

        assert result == expected

def test_add_book(client):
    search_term = '1234567890'
    stock = 10
    price = 19.99
    mock_book_data = (
        search_term, 'Test Book', 'Author One, Author Two', 300, 'Test Publisher',
        '2023-01-01', 'http://example.com/thumbnail.jpg', 'http://example.com/cover.jpg'
    )

    with patch('Novel_Solutions.blueprints.inventory.Novel_inventory.get_book_data') as mock_get_book_data:
        mock_get_book_data.return_value = mock_book_data

        response = client.post('/add_book', data={
            'search_term': search_term,
            'stock': stock,
            'price': price
        })

        assert response.status_code == 200
        assert b'Book added to inventory.' in response.data

        book = Book.query.filter_by(isbn=search_term).first()
        assert book is not None
        assert book.title == 'Test Book'
        assert book.authors == 'Author One, Author Two'
        assert book.number_of_pages == 300
        assert book.publishers == 'Test Publisher'
        assert book.publish_date == '2023-01-01'
        assert book.thumbnail_url == 'http://example.com/thumbnail.jpg'
        assert book.cover == 'http://example.com/cover.jpg'
        assert book.stock == stock
        assert book.price == price

def test_search_book_found(client):
    # Add a book to the database
    book = Book(isbn='1234567890', sku='SKU1', title='Test Book', stock=10, price=19.99)
    db.session.add(book)
    db.session.commit()

    # Simulate a POST request to the /search route
    response = client.post('/search', data={'search_term': '1234567890'})

    # Verify that the correct template is rendered and the book data is displayed
    assert response.status_code == 200
    assert b'Test Book' in response.data
    assert b'1234567890' in response.data

def test_search_book_not_found(client):
    # Simulate a POST request to the /search route with a non-existent book
    response = client.post('/search', data={'search_term': '0000000000'})

    # Verify that the correct template is rendered and an appropriate flash message is displayed
    assert response.status_code == 200
    assert b'Book not found In Inventory.' in response.data

def test_inventory_authenticated(client):
    # Create a test user and log them in
    user = User(username='testuser', email='test@example.com', password='password')
    db.session.add(user)
    db.session.commit()
    login_user(user)

    # Add a book to the database
    book = Book(isbn='1234567890', sku='SKU1', title='Test Book', stock=10, price=19.99)
    db.session.add(book)
    db.session.commit()

    # Simulate a GET request to the /inventory route
    response = client.get('/inventory')

    # Verify that the correct template is rendered and the book data is displayed
    assert response.status_code == 200
    assert b'Test Book' in response.data
    assert b'1234567890' in response.data

    # Log out the user
    logout_user()

def test_inventory_not_authenticated(client):
    # Simulate a GET request to the /inventory route without logging in
    response = client.get('/inventory')

    # Verify that the user is redirected to the login page
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
