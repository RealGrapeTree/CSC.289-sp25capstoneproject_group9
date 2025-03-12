import pytest
from models import Book, Inventory
from app import app, db
from blueprints.inventory.Novel_inventory import Novel_inventory, insert_book_into_db, add_book

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def create_new_book():
    new_book = Book(isbn="0375826696", title="Eragon", authors="Christopher Paolini", sku=None, stock=10,
                    price=9.99, number_of_pages=503, publishers="KNOPF", publish_date="2003",
                    thumbnail_url=None, cover=None)
    return new_book



