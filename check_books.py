import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('books.db')
cursor = conn.cursor()

# Query all books
cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()

# Print all rows in the books table
for row in rows:
    print(row)

conn.close()
