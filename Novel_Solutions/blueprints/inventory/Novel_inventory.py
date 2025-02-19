from flask import request, jsonify, Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import requests
from extensions import db
from models import Book
from flask_login import login_required, current_user



Novel_inventory = Blueprint('Novel_inventory', __name__, template_folder='templates')


# Route to search for a book by ISBN or SKU
@Novel_inventory.route('/book_search/<isbn>', methods=['POST'])
@login_required
def book_search(isbn):

    # Check if the user is logged in
    if current_user.is_authenticated:

       
        book = Book.query.filter((Book.isbn == isbn) | (Book.sku == isbn)).first()

        # Check if the book exists within database
        if book:
            # return the book data as a JSON response
            return jsonify(
                    {
                        "isbn"  : book.isbn,
                        "title" : book.title,
                        "authors" : book.authors,
                        "number_of_pages" : book.number_of_pages,   
                        "publishers" : book.publishers,
                        "publish_date" : book.publish_date,
                        "thumbnail_url" : book.thumbnail_url,
                        "cover" : book.cover
                    }), 201
            
        # Fetch book data from Open Library API if not found within database
        else:
            # Fetch book data from Open Library API
            isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover = get_book_data(isbn)
                
            # if book was found insert into database and return a the book in JSON
            if isbn:
                new_book = insert_book_into_db(isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover)

                return jsonify(
                    {
                        "isbn"  : new_book.isbn,
                        "title" : new_book.title,
                        "authors" : new_book.authors,
                        "number_of_pages" : new_book.number_of_pages,   
                        "publishers" : new_book.publishers,
                        "publish_date" : new_book.publish_date,
                        "thumbnail_url" : new_book.thumbnail_url,
                        "cover" : new_book.cover
                    }), 201
            else:
                return jsonify({'message': 'Book not found.'}), 404

    return jsonify({'message': 'User not logged in.'}), 401


# Function to fetch book data from Open Library API using ISBN
def get_book_data(isbn):
    url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'
    response = requests.get(url)
    data = response.json()

    book_info = data.get(f'ISBN:{isbn}')
    if book_info:
        title = book_info.get('title', 'Unknown Title')
        authors = ', '.join([author['name'] for author in book_info.get('authors', [])])
        number_of_pages = book_info.get('number_of_pages', 'Unknown')
        publishers = ', '.join([publisher['name'] for publisher in book_info.get('publishers', [])])
        publish_date = book_info.get('publish_date', 'Unknown')
        thumbnail_url = book_info.get('cover', {}).get('medium', 'Unknown')
        cover = book_info.get('cover', {}).get('large', 'Unknown')


        return isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover, 
    return None, None, None, None, None, None, None, None



# Function to insert book data into the database using SQLAlchemy
def insert_book_into_db(isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover):
    new_book = Book(isbn=isbn, title=title, authors=authors, sku=None, stock=10, price=19.99 , number_of_pages=number_of_pages, publishers=publishers, publish_date=publish_date, thumbnail_url=thumbnail_url, cover=cover)
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



