import requests
import sqlite3

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

# Function to insert book data into SQLite
def insert_book_into_db(isbn, title, authors):
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    # Inserting book data into the books table
    cursor.execute('''
        INSERT INTO books (isbn, title, sku, stock, price)
        VALUES (?, ?, ?, ?, ?)
    ''', (isbn, title, '', 10, 19.99))  # Use default values for sku, stock, price

    conn.commit()
    conn.close()

# Example usage: insert books into SQLite by querying the API with ISBNs
isbns = ['9780140449136', '9780135166307']  # Example ISBNs
for isbn in isbns:
    isbn, title, authors = get_book_data(isbn)
    if isbn:
        insert_book_into_db(isbn, title, authors)
        print(f"Inserted: {title} by {authors}")
