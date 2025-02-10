# Novel Solution

A Novel Solution aims to provide an efficient system for managing bookstore 
inventory and point-of-sale (POS) operations.

## Install Dependencies:
Run pip install -r requirements.txt to install required libraries (requests).

## Setup SQLite Database:
Run python setup_db.py to create the books table in the books.db SQLite database.

## Populate Database:
Run python fetch_books_from_api.py to fetch book data from the Open Library API and insert it into the database.

## Search for Books:
Run python book-search.py to search for books by ISBN in the database. The script will display book details (title, stock, price) if found.
