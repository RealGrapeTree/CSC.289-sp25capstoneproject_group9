
# If there's an internal server error, 
# run the command in the terminal: docker exec -it novel_solutions flask shell
# Then in the shell, add: 
# from app import db
# db.create_all()
# exit() 

import pytest
from unittest.mock import patch
from flask import session
from app import app, db
from models import Book, Transaction, User
from blueprints.POS.Novel_POS import save_transaction_to_db, update_inventory_after_sale
from flask_login import login_user

# test_app.py
import pytest
from werkzeug.security import generate_password_hash
from extensions import bcrypt
import requests
from unittest.mock import patch, MagicMock
from flask import request, Flask, g, template_rendered
from flask_login import LoginManager, login_required, current_user
from blueprints.loginpage.Novel_login import Novel_login, login_user, logout_user
from app import app, db, create_default_manager
from models import User, Transaction, TransactionItem, Book
from contextlib import contextmanager
from blueprints.inventory.Novel_inventory import Novel_inventory, check_books, insert_book_into_db, get_book_data, add_book, inventory


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    app.config['SECRET_KEY'] = 'testkey'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add a sample book
            book = Book(id=1, isbn="1234567890", title="Test Book", stock=10, price=15.99)
            db.session.add(book)
            db.session.commit()
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            create_default_manager()
            
        yield client
        with app.app_context():
            db.drop_all()



def test_save_transaction_to_db(client):
    with app.app_context():
        cart = {"1": 2}
        save_transaction_to_db(user_id="admin", amount=31.98, status="completed", stripe_payment_id="pi_12345", cart=cart)
        tx = Transaction.query.first()
        assert tx is not None
        assert tx.user_id == "admin"
        assert tx.amount == 31.98


def test_update_inventory_after_sale(client):
    with app.app_context():
        cart = {"1": 2}
        update_inventory_after_sale(cart)
        book = db.session.get(Book, 1)
        assert book.stock == 8

@patch("blueprints.POS.Novel_POS.stripe.PaymentIntent.create")
def test_create_payment_intent(mock_create, client):
    with app.app_context():
        user = User(username='admin', password='admin123', role='manager',
                    firstname='Admin', lastname='User', email="admin@example.com")
        db.session.add(user)
        db.session.commit()

        with app.test_request_context():  
            login_user(user)

        with client.session_transaction() as sess:
            sess['cart'] = {'1': 2}
            sess['_user_id'] = user.get_id() 

    mock_create.return_value = type('obj', (object,), {
        'id': 'pi_123',
        'client_secret': 'secret_123'
    })()

    response = client.post("/create-payment-intent", json={"amount": 1000})
    print(response.data.decode())
    assert response.status_code == 200
    assert b"clientSecret" in response.data



@patch("blueprints.POS.Novel_POS.save_transaction_to_db")
def test_cash_checkout(mock_save, client):
    with app.app_context():
        # Create and add user
        user = User(
            username='admin',
            password='admin123',
            role='manager',
            firstname='Admin',
            lastname='User',
            email='admin@example.com'
        )
        db.session.add(user)
        db.session.commit()

        # Make login_user work by entering request context
        with app.test_request_context():
            login_user(user)

        # Add cart to session
        with client.session_transaction() as sess:
            sess['cart'] = {'1': 1}
            sess['_user_id'] = user.get_id()  # important if using username as ID

    # Mock DB save method
    mock_save.return_value = None

    # Perform request
    response = client.get("/cash_checkout")

    # Assertions
    assert response.status_code == 200


def test_send_email_receipt(client):
    response = client.post("/send-receipt/email", json={"email": "test@example.com"})
    assert response.status_code == 200
    assert b"Receipt sent to test@example.com!" in response.data


def test_send_sms_receipt(client):
    response = client.post("/send-receipt/sms", json={"phone": "+1234567890"})
    assert response.status_code == 200
    assert b"Receipt sent via SMS to +1234567890!" in response.data


@patch("blueprints.POS.Novel_POS.stripe.Refund.create")
def test_refund_success(mock_refund, client):
    with client.application.app_context():
        transaction = Transaction(
            user_id="admin",
            amount=1000,
            status="completed",
            stripe_payment_id="pi_123"
        )
        db.session.add(transaction)
        db.session.commit()

        transaction_id = transaction.id

    mock_refund.return_value = {"id": "re_123"}

    response = client.post(f"/refund/{transaction_id}")
    assert response.status_code == 302  # assuming it redirects after refund
=======
def login(client, username):
    with client.session_transaction() as session:
        user = User.query.filter_by(username=username).first()
        g.user = user
        


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



def test_check_books(capsys, client):
    """Test that check_books() prints all books correctly"""
    # Create mock books
    mock_book1 = MagicMock()
    mock_book1.id = 1
    mock_book1.isbn = "1234567890"
    mock_book1.sku = "SKU001"
    mock_book1.title = "Test Book 1"
    mock_book1.stock = 5
    mock_book1.price = 12.99

    mock_book2 = MagicMock()
    mock_book2.id = 2
    mock_book2.isbn = "0987654321"
    mock_book2.sku = "SKU002"
    mock_book2.title = "Test Book 2"
    mock_book2.stock = 3
    mock_book2.price = 9.99

    # Mock the Book.query.all() within an application context
    with client.application.app_context():
        with patch('blueprints.inventory.Novel_inventory.Book.query') as mock_query:
            mock_query.all.return_value = [mock_book1, mock_book2]
            
            # Call the function
            check_books()
            
            # Capture the printed output
            captured = capsys.readouterr()
            output = captured.out

    # Verify the output contains expected lines
    assert "ID: 1, ISBN: 1234567890, SKU: SKU001, Title: Test Book 1, Stock: 5, Price: $12.99" in output
    assert "ID: 2, ISBN: 0987654321, SKU: SKU002, Title: Test Book 2, Stock: 3, Price: $9.99" in output


def test_check_books_empty(capsys, client):
    """Test that check_books() handles empty database correctly"""
    with client.application.app_context():
        with patch('blueprints.inventory.Novel_inventory.Book.query') as mock_query:
            mock_query.all.return_value = []
            
            # Clear any existing captured output
            capsys.readouterr()
            
            check_books()
            
            captured = capsys.readouterr()
            # Check that check_books() specifically didn't print anything
            assert captured.out == ""

"""
*
* Tests for add_book functionality
*
"""

def test_add_book_requires_login(client):
    """Test that add_book route requires login"""
    response = client.get('/add_book', follow_redirects=False)
    assert response.status_code == 302  # Should redirect to login

def test_add_book_get_request(client):
    """Test GET request to add_book shows the form"""
    # Login as manager first
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    response = client.get('/add_book')
    assert response.status_code == 200
    assert b'Add Book to Inventory' in response.data

@patch('blueprints.inventory.Novel_inventory.get_book_data')
def test_add_book_existing_in_db(mock_get_data, client):
    """Test adding a book that already exists in database"""
    # Login as manager first
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    # Create a test book in database
    test_book = Book(
        isbn='1234567890',
        title='Existing Book',
        authors='Test Author',
        stock=5,
        price=10.99
    )
    db.session.add(test_book)
    db.session.commit()
    
    # Try to add the same book
    response = client.post('/add_book', data={
        'search_term': '1234567890',
        'stock': '10',
        'price': '12.99'
    }, follow_redirects=True)
    
    # Should show the existing book
    assert response.status_code == 200
    assert b'Existing Book' in response.data
    # Shouldn't call the API
    mock_get_data.assert_not_called()

@patch('blueprints.inventory.Novel_inventory.requests.get')
def test_add_book_via_isbn(mock_get, client):
    """Test adding a new book via ISBN lookup"""
    # Login as manager first
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'ISBN:1234567890': {
            'title': 'Test Book',
            'authors': [{'name': 'Author One'}, {'name': 'Author Two'}],
            'number_of_pages': 300,
            'publishers': [{'name': 'Test Publisher'}],
            'publish_date': '2020-01-01',
            'cover': {'large': 'http://example.com/large.jpg'},
            'thumbnail_url': 'http://example.com/thumb.jpg'
        }
    }
    mock_get.return_value = mock_response
    
    response = client.post('/add_book', data={
        'search_term': '1234567890',
        'stock': '5',
        'price': '15.99'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test Book' in response.data
    assert b'Author One, Author Two' in response.data
    assert b'15.99' in response.data
    
    # Verify book was added to database
    book = Book.query.filter_by(isbn='1234567890').first()
    assert book is not None
    assert book.title == 'Test Book'

@patch('blueprints.inventory.Novel_inventory.requests.get')
def test_add_book_not_found_shows_manual_form(mock_get, client):
    """Test that when book isn't found, manual form is shown for managers"""
    # Login as manager first
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    # Mock API not finding the book
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response
    
    response = client.post('/add_book', data={
        'search_term': '0000000000',
        'stock': '5',
        'price': '15.99'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Book Not Found - Please Enter Details Manually' in response.data
    assert b'value="0000000000"' in response.data  # ISBN should be pre-filled

def test_add_book_manual_non_manager(client):
    """Test that non-managers can't access manual add form"""
    # 1. Create cashier directly in database
    with client.application.app_context():
        cashier = User(
            username='cashier1',
            firstname='John',
            lastname='James',
            email='james@example.com',
            password=bcrypt.generate_password_hash('cashier1').decode('utf-8'),
            role='cashier'
        )
        db.session.add(cashier)
        db.session.commit()
    
    # 2. Login as cashier - don't follow redirects
    login_response = client.post('/login', data={
        'username': 'cashier1',
        'password': 'cashier1'
    }, follow_redirects=False)
    assert login_response.status_code == 302  # Should redirect
    
    # 3. Get session cookie and proceed directly to add_book
    session_cookie = login_response.headers.get('Set-Cookie')
    
    # 4. Attempt manual add with authenticated session
    response = client.post('/add_book', data={
        'manual_add': 'true',
        'title': 'Test Book',
        'authors': 'Test Author',
        'stock': '5',
        'price': '15.99'
    }, headers={'Cookie': session_cookie}, follow_redirects=True)
    
    # 5. Verify permission error
    assert b'Only managers can add books manually' in response.data
def test_add_book_manual_success(client):
    """Test successful manual book addition by manager"""
    # Login as manager first
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    response = client.post('/add_book', data={
        'manual_add': 'true',
        'isbn': '1234567890',
        'title': 'Manual Book',
        'authors': 'Manual Author',
        'number_of_pages': '200',
        'publishers': 'Manual Publisher',
        'publish_date': '2021-01-01',
        'thumbnail_url': 'http://example.com/thumb.jpg',
        'cover': 'http://example.com/cover.jpg',
        'stock': '10',
        'price': '19.99'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Manual Book' in response.data
    assert b'Manual Author' in response.data
    assert b'19.99' in response.data
    
    # Verify book was added to database
    book = Book.query.filter_by(isbn='1234567890').first()
    assert book is not None
    assert book.title == 'Manual Book'

def test_add_book_manual_missing_required(client):
    """Test manual book addition with missing required fields"""
    # Login as manager first
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    response = client.post('/add_book', data={
        'manual_add': 'true',
        'isbn': '1234567890',
        # Missing title and authors
        'stock': '10',
        'price': '19.99'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Title and Authors are required fields' in response.data
    # Should show the form again
    assert b'Book Not Found - Please Enter Details Manually' in response.data


def test_inventory_comprehensive(client):
    """Test all inventory scenarios in one function"""
    # 1. Setup test data
    with app.app_context():
        # Clear existing and add test books
        Book.query.delete()
        books = [
            Book(isbn="111", title="Book 1", stock=5, price=10.99),
            Book(isbn="222", title="Book 2", stock=3, price=15.99),
            *[Book(isbn=str(i), title=f"Book {i}", stock=i, price=i*5) for i in range(3, 12)]
        ]
        db.session.add_all(books)
        db.session.commit()

    # 2. Test unauthenticated access
    response = client.get('/inventory', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

    # 3. Test authenticated access
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    # 4. Test page 1 (alphabetical order: 1, 10, 11, 2, 3, 4, 5, 6, 7, 8)
    response = client.get('/inventory')
    assert response.status_code == 200
    assert b'Book 1' in response.data  # First book alphabetically
    assert b'Book 8' in response.data  # Last on page 1 (10 books per page)
    assert b'page=2' in response.data  # Pagination control

    # 5. Test page 2 (alphabetical order: 9)
    response = client.get('/inventory?page=2')
    assert b'Book 9' in response.data  # Only book on page 2
    assert b'page=1' in response.data  # Previous page link

    # 6. Test empty inventory
    with app.app_context():
        Book.query.delete()
        db.session.commit()
    
    response = client.get('/inventory')
    assert b'Page 1 of 0' in response.data  # Pagination empty state
    assert b'<table>' not in response.data  # Table should be hidden

def test_search(client):
    """Test all search scenarios in one function"""
    # Setup - create test book and login
    with app.app_context():
        test_book = Book(isbn="1234567890", sku="BOOK123", title="Test Book", stock=5, price=10.99)
        db.session.add(test_book)
        db.session.commit()
    
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})

    # Test 1: Search by ISBN (found)
    response = client.post('/search', data={'search_term': '1234567890'})
    assert b'Test Book' in response.data
    assert b'Search Results' in response.data  # Verify results table appears

    # Test 2: Search by SKU (found)
    response = client.post('/search', data={'search_term': 'BOOK123'})
    assert b'Test Book' in response.data
    assert b'Search Results' in response.data  # Verify results table appears

    # Test 3: Not found
    response = client.post('/search', data={'search_term': '0000000000'})
    assert response.status_code == 200
    assert b'Book not found in inventory.' in response.data  # More generic assertion for flash message
    assert b'Search Results' not in response.data  # Verify results table doesn't appear

    # Test 4: Unauthenticated access
    client.get('/logout')
    response = client.get('/search', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

def test_update_book(client):
    """Test book update functionality with manager permissions"""
    # Setup - create test book and login as admin (manager)
    with app.app_context():
        Book.query.delete()
        test_book = Book(
            isbn="1234567890",
            title="Original Title",
            authors="Original Author",  # Added initial author
            stock=5,
            price=10.99
        )
        db.session.add(test_book)
        db.session.commit()
        book_id = test_book.id
    
    # Login as admin (manager role)
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})

    # Test 1: Verify form shows current data
    response = client.get(f'/update_book/{book_id}')
    assert response.status_code == 200
    assert b'Original Title' in response.data
    assert b'Original Author' in response.data  # Verify author field
    assert b'value="5"' in response.data  # Stock
    assert b'value="10.99"' in response.data  # Price

    # Test 2: Successful update of all fields
    updated_data = {
        'title': 'Updated Title',
        'authors': 'Updated Author',  # Include authors in test data
        'stock': '10',
        'price': '19.99'
    }
    response = client.post(f'/update_book/{book_id}', data=updated_data, follow_redirects=True)
    
    # Verify redirect and flash message
    assert response.status_code == 200
    assert b'Inventory' in response.data
    assert b'Success!' in response.data
    assert b'Updated Title' in response.data

    print(response.data.decode())
    
    # Verify all fields in database
    with app.app_context():
        updated_book = db.session.get(Book, book_id)  # Updated to SQLAlchemy 2.0 style
        assert updated_book.title == 'Updated Title'
        assert updated_book.authors == 'Updated Author'  # Now should pass
        assert updated_book.stock == 10
        assert float(updated_book.price) == 19.99

    # Test 3: Invalid stock (negative)
    response = client.post(f'/update_book/{book_id}', data={
        'title': 'Test Title',
        'authors': 'Test Author',
        'stock': '-1',
        'price': '10.99'
    })
    assert response.status_code == 200
    assert b'Stock cannot be negative' in response.data
    #assert b'value="-1"' in response.data  # Form retains invalid input

    # Test 4: Invalid price (non-numeric)
    response = client.post(f'/update_book/{book_id}', data={
        'title': 'Test Title',
        'authors': 'Test Author',
        'stock': '5',
        'price': 'invalid'
    })
    assert response.status_code == 200
    assert b'Price must be a number' in response.data

    # Test 5: Non-manager access
    # Create and login as a non-manager user
    with app.app_context():
        User.query.filter_by(username='staff').delete()
        hashed_password = bcrypt.generate_password_hash('staff123').decode('utf-8')
        staff = User( username='staff',
            password=hashed_password,
            role='staff',
            firstname='Test',
            lastname='User',
            email='staff@example.com')
        db.session.add(staff)
        db.session.commit()
    
    client.get('/logout')
    client.post('/login', data={'username': 'staff', 'password': 'staff123'})
    response = client.get(f'/update_book/{book_id}', follow_redirects=True)
    assert b'You do not have permission' in response.data


def test_delete_book(client):
    """Test book deletion functionality with manager permissions"""
    # Setup - create test book
    with app.app_context():
        db.session.query(Book).delete()
        test_book = Book(
            isbn="1234567890",
            title="Test Book",
            authors="Test Author",
            stock=10,
            price=19.99
        )
        db.session.add(test_book)
        db.session.commit()
        book_id = test_book.id
    
    # Test 1: Unauthenticated access (should redirect to login)
    response = client.post(f'/delete_book/{book_id}', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

    # Test 2: Non-manager access (staff user)
    with app.app_context():
        # Create and login as staff user
        staff = User(
            username='staff',
            password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
            role='staff',
            firstname='Staff',
            lastname='User',
            email='staff@example.com'
        )
        db.session.add(staff)
        db.session.commit()
    
    client.post('/login', data={'username': 'staff', 'password': 'staff123'})
    response = client.post(f'/delete_book/{book_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'You do not have permission' in response.data
    
    # Verify book was NOT deleted
    with app.app_context():
        book = db.session.get(Book, book_id)
        assert book.stock == 10  # Stock unchanged

    # Test 3: Manager successful deletion
    client.get('/logout')
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    # Verify pre-deletion state
    with app.app_context():
        book = db.session.get(Book, book_id)
        assert book.stock == 10
    
    response = client.post(f'/delete_book/{book_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Book removed from inventory' in response.data
    assert b'Inventory' in response.data  # Verify redirect to inventory page
    
    # Verify soft-delete (stock=0)
    with app.app_context():
        book = db.session.get(Book, book_id)
        assert book.stock == 0

    # Test 4: Delete non-existent book
    response = client.post('/delete_book/9999', follow_redirects=True)
    assert response.status_code == 404
    
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








