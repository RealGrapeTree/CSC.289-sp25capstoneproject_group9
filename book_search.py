import sqlite3
import tkinter as tk
from tkinter import messagebox

def search_book(search_term):
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    query = '''SELECT * FROM books WHERE isbn=? OR sku=?'''
    cursor.execute(query, (search_term, search_term))
    result = cursor.fetchone()
    conn.close()
    return result

def show_book_details(book):
    if book:
        details = f"Title: {book[3]}\nStock: {book[4]}\nPrice: ${book[5]:.2f}"
        messagebox.showinfo("Book Details", details)
    else:
        messagebox.showerror("Error", "Book not found.")

def search_button_click():
    search_term = entry.get()
    book = search_book(search_term)
    show_book_details(book)

# Tkinter GUI
root = tk.Tk()
root.title("Book Search")

label = tk.Label(root, text="Enter ISBN or SKU:")
label.pack()

entry = tk.Entry(root)
entry.pack()

search_button = tk.Button(root, text="Search", command=search_button_click)
search_button.pack()

root.mainloop()
