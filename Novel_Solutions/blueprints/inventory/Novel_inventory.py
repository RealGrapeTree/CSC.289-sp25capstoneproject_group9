from flask import request, jsonify, Blueprint, request, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy

import requests
from extensions import db
from models import Book
from flask_login import login_required, current_user


Novel_inventory = Blueprint('Novel_inventory', __name__, template_folder='templates')


# Route to search for a book by ISBN or SKU
@Novel_inventory.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():

    # Check if the user is logged in
    if current_user.is_authenticated:

        # Get the search term from the form
        if request.method == 'POST':
            search_term = request.form['search_term']
            book = Book.query.filter((Book.isbn == search_term) | (Book.sku == search_term)).first()

            # Check if the book exists within database
            if book:
                # Render the inventory.html template with the book data
                return render_template('inventory.html', book=book, username=current_user.username)
            
            # Fetch book data from Open Library API if not found within database
            else:
                # Fetch book data from Open Library API
                isbn, title, authors= get_book_data(search_term)
                
                # if book was found insert into database
                if isbn:
                    new_book = insert_book_into_db(isbn, title, authors)

                    return render_template('inventory.html', book=new_book , user=current_user.username)
                else:
                    flash('Book not found.', 'danger')

        return render_template('inventory.html', user=current_user.username)


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
    new_book = Book(isbn=isbn, title=title, authors=authors, sku=None, stock=10, price=19.99)
    db.session.add(new_book)
    db.session.commit()
    return new_book



# maybe use this function to show all books in inventory

# Function to check all books in the database
def check_books():
    books = Book.query.all()
    for book in books:
        print(f"ID: {book.id}, ISBN: {book.isbn}, SKU: {book.sku}, Title: {book.title}, Stock: {book.stock}, Price: ${book.price:.2f}")






def fetch_and_insert_books():
    # List of ISBNs to fetch
        isbns = ['9780140449136', '9780135166307']
        for isbn in isbns:
            fetched_isbn, title, authors = get_book_data(isbn)
            if fetched_isbn:
                insert_book_into_db(fetched_isbn, title, authors)
                print(f"Inserted: {title} by {authors}")
            else:
                print(f"No data found for ISBN: {isbn}")



