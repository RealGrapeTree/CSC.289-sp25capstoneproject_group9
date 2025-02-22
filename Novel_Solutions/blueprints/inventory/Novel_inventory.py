from flask import request, jsonify, Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import requests
from extensions import db
from models import Book
from flask_login import login_required, current_user



Novel_inventory = Blueprint('Novel_inventory', __name__, template_folder='templates')





# Function to insert book data into the database using SQLAlchemy
def insert_book_into_db(isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover, stock=10, price=19.99):
    new_book = Book(isbn=isbn, title=title, authors=authors, sku=None, stock=stock, price=price , number_of_pages=number_of_pages, publishers=publishers, publish_date=publish_date, thumbnail_url=thumbnail_url, cover=cover)
    db.session.add(new_book)
    db.session.commit()
    return new_book




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


        return isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover
    return None, None, None, None, None, None, None, None




# use this function in a show all inventory page
# Function to check all books in the database
def check_books():
    books = Book.query.all()
    for book in books:
        print(f"ID: {book.id}, ISBN: {book.isbn}, SKU: {book.sku}, Title: {book.title}, Stock: {book.stock}, Price: ${book.price:.2f}")






# Route to add a book to the database by ISBN
# also add price and stock for each book in JSON format
# checks if the book exists within the database if not fetches the book data from the Open Library API and adds it 
@Novel_inventory.route('/add_book', methods=['POST'])
@login_required
def book_search():

    # Check if the user is logged in
    if current_user.is_authenticated:

        # TODO:  add a way to update the stock and price of each book added to database
        
        # Get the ISBN from the request
        isbn = request.json.get('isbn')
        # Get the stock and price from the request
        stock = request.json.get('stock')
        price = request.json.get('price')
       
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
                        "cover" : book.cover,
                        "stock" : book.stock,
                        "price" : book.price
                    }), 201
            
        # Fetch book data from Open Library API if not found within database
        else:
            # Fetch book data from Open Library API
            isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover = get_book_data(isbn)
                
            # if book was found insert into database and return a the book in JSON
            if isbn:
                new_book = insert_book_into_db(isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover, stock, price)

                return jsonify(
                    {
                        "isbn"  : new_book.isbn,
                        "title" : new_book.title,
                        "authors" : new_book.authors,
                        "number_of_pages" : new_book.number_of_pages,   
                        "publishers" : new_book.publishers,
                        "publish_date" : new_book.publish_date,
                        "thumbnail_url" : new_book.thumbnail_url,
                        "cover" : new_book.cover,
                        "stock" : new_book.stock,
                        "price" : new_book.price
                    }), 201
            else:
                return jsonify({'message': 'Book not found.'}), 404

    return jsonify({'message': 'User not logged in.'}), 401



@Novel_inventory.route('/delete_book/<isbn>', methods=['DELETE'])
@login_required
# add route to delete a book from the database
# if book is deleted return a message as a JSON response
def delete_book(isbn):
    pass


@Novel_inventory.route('/update_book_stock', methods=['PUT'])
@login_required 
# add route to update a book in the database
# if book is updated return a message as a JSON response
def update_book_stock():
    # use request.json.get('isbn') to get isbn adn request.json.get('stock') to get stock
    pass

@Novel_inventory.route('/update_book_price', methods=['PUT'])
@login_required
# add route to update a book in the database
# if book is updated return a message as a JSON response
def update_book_price():
    # user request.json.get('isbn') to get isbn and request.json.get('price') to get price
    pass



@Novel_inventory.route('/search_book/<isbn>', methods=['POST'])
# add route to search if a book is within the database
# if book is found  within database return the book data as a JSON response
# if book is not found within database return a message as a JSON response
def search_book():
    pass





@Novel_inventory.route('/inventory', methods=['GET'])
@login_required
def inventory():
    pass
# add route to show all books in the database
