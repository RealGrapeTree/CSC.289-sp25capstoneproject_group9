import pytest
from app import app, db, User
from werkzeug.security import generate_password_hash

# Test Client setup
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory DB for testing
    db.create_all()

    # Create test users
    cashier = User(username="cashier_user", password_hash=generate_password_hash("cashierpassword"), role="cashier")
    manager = User(username="manager_user", password_hash=generate_password_hash("managerpassword"), role="manager")
    db.session.add(cashier)
    db.session.add(manager)
    db.session.commit()

    with app.test_client() as client:
        yield client

    db.drop_all()

# Test Cashier Access
def test_cashier_access(client):
    # Log in as cashier
    response = client.post('/login', data={'username': 'cashier_user', 'password': 'cashierpassword'})
    assert response.status_code == 200
    assert b'Process Sale' in response.data

    # Try accessing restricted page (should be accessible)
    response = client.get('/process_sale')
    assert response.status_code == 200

# Test Manager Access (Should be denied access to process sale)
def test_manager_access(client):
    # Log in as manager
    response = client.post('/login', data={'username': 'manager_user', 'password': 'managerpassword'})
    assert response.status_code == 200

    # Try accessing restricted page (should be unauthorized)
    response = client.get('/process_sale')
    assert response.status_code == 302  # Should redirect
    assert b'Unauthorized! Only cashiers can process sales.' in response.data

# Test Unauthorized User Access to Process Sale
def test_unauthorized_user_access(client):
    # Log in as an invalid user
    response = client.post('/login', data={'username': 'nonexistent_user', 'password': 'wrongpassword'})
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
