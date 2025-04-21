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
