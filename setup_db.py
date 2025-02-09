import sqlite3

def create_books_table():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    # Creating the books table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        isbn TEXT,
        sku TEXT,
        title TEXT,
        stock INTEGER,
        price REAL
    );
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_books_table()
    print("Books table created successfully.")
