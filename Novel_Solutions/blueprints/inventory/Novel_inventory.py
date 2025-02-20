from flask import request, jsonify, Blueprint, render_template, flash
import requests
from extensions import db
from models import Book
from flask_login import login_required, current_user

Novel_inventory = Blueprint('Novel_inventory', __name__, template_folder='templates')

# ✅ Route to display both the book inventory and search results
@Novel_inventory.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    books = Book.query.all()  # Fetch all books from the database
    search_result = None

    if request.method == 'POST':
        search_term = request.form['search_term']
        search_result = Book.query.filter((Book.isbn == search_term) | (Book.sku == search_term)).first()

        if not search_result:
            isbn, title, authors = get_book_data(search_term)
            if isbn:
                search_result = insert_book_into_db(isbn, title, authors)
            else:
                flash('Book not found.', 'danger')

    return render_template('inventory.html', books=books, search_result=search_result, username=current_user.username)

# ✅ Fetch book data from Open Library API using ISBN
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

# ✅ Insert book data into the database
def insert_book_into_db(isbn, title, authors):
    new_book = Book(isbn=isbn, title=title, authors=authors, sku=None, stock=10, price=19.99)
    db.session.add(new_book)
    db.session.commit()
    return new_book
