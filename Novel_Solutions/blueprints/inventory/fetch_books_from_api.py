import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Novel_inventory import Novel_inventory
from extensions import db

# # Initialize Flask and SQLAlchemy
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# Define the Book model (ensure it matches your database schema)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    sku = db.Column(db.String(20), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)

# Function to fetch book data from Open Library API using ISBN
def get_book_data(isbn):
    url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'
    response = requests.get(url)
    data = response.json()

    book_info = data.get(f'ISBN:{isbn}')
    if book_info:
        title = book_info.get('title', 'Unknown Title')
        authors = ', '.join([author['name'] for author in book_info.get('authors', [])])
        return isbn, title, authors
    return None, None, None

# Function to insert book data into the database using SQLAlchemy
def insert_book_into_db(isbn, title, authors):
    new_book = Book(isbn=isbn, title=title, sku=None, stock=10, price=19.99)
    db.session.add(new_book)
    db.session.commit()

# Example usage: fetch and insert books from the API
if __name__ == '__main__':
    with app.app_context():
        # List of ISBNs to fetch
        isbns = ['9780140449136', '9780135166307']
        for isbn in isbns:
            fetched_isbn, title, authors = get_book_data(isbn)
            if fetched_isbn:
                insert_book_into_db(fetched_isbn, title, authors)
                print(f"Inserted: {title} by {authors}")
            else:
                print(f"No data found for ISBN: {isbn}")
