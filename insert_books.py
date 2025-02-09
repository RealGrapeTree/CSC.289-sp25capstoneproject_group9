import sqlite3

def insert_book(isbn, sku, title, stock, price):
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO books (isbn, sku, title, stock, price)
        VALUES (?, ?, ?, ?, ?)
    ''', (isbn, sku, title, stock, price))

    conn.commit()
    conn.close()

# Example book entries
insert_book('978-1234567890', 'SKU001', 'Book Title 1', 10, 19.99)
insert_book('978-0987654321', 'SKU002', 'Book Title 2', 5, 29.99)

print("Books inserted!")
