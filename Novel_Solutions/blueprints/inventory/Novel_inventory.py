from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for
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



# ✅ Fetch book data from Open Library API using ISBN
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





# Route to search for a book by ISBN or SKU
@Novel_inventory.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():

    # Check if the user is logged in
    if current_user.is_authenticated:

        # Get the search term from the form
        if request.method == 'POST':
            search_term = request.form['search_term']
            stock = request.form['stock']
            price = request.form['price']
            book = Book.query.filter((Book.isbn == search_term) | (Book.sku == search_term)).first()

            # Check if the book exists within database
            if book:
                # Render the inventory.html template with the book data
                return render_template('add_book.html', book=book, user=current_user)
            
            # Fetch book data from Open Library API if not found within database
            else:
                # Fetch book data from Open Library API
                isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover = get_book_data(search_term)
                
                # if book was found insert into database
                if isbn:
                    flash('Book added to inventory.', 'success')
                    new_book = insert_book_into_db(isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover, stock, price)

                    return render_template('add_book.html', book=new_book , user=current_user)
                else:
                    flash('Book not found.', 'danger')

        return render_template('add_book.html', user=current_user)
    

@Novel_inventory.route('/inventory', methods=['GET'])
@login_required
def inventory():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of items per page
        
        # Get paginated books
        books_pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
        books = books_pagination.items
        
        return render_template('inventory.html', 
                             books=books, 
                             pagination=books_pagination,
                             user=current_user.username)
    else:
        return redirect(url_for('Novel_login.login'))
        
    
@Novel_inventory.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    # Check if the user is logged in
    if current_user.is_authenticated:

        # Get the search term from the form
        if request.method == 'POST':
            search_term = request.form['search_term']
            book = Book.query.filter((Book.isbn == search_term) | (Book.sku == search_term)).first()
            if book:
                return render_template('search.html', book=book, user=current_user)
            if not book:
                flash('Book not found in inventory.', 'danger')
                return render_template('search.html', user=current_user)
    
  
    return render_template('search.html', user=current_user)


# Route to update book details
@Novel_inventory.route('/update_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)

    if current_user.role != "manager":
        flash("You do not have permission to update books.", "danger")
        return redirect(url_for('Novel_inventory.inventory'))

    if request.method == 'POST':
        book.title = request.form['title']
        has_error = False

        # Validate stock
        try:
            stock = int(request.form['stock'])
            if stock < 0:
                flash("Stock cannot be negative", "stock_error")
                has_error = True
            else:
                book.stock = stock
        except ValueError:
            flash("Stock must be a whole number", "stock_error")
            has_error = True

        # Validate price
        try:
            price = round(float(request.form['price']), 2)
            if price < 0:
                flash("Price cannot be negative", "price_error")
                has_error = True
            else:
                book.price = "{:.2f}".format(price)
        except ValueError:
            flash("Price must be a number (e.g. 12.99)", "price_error")
            has_error = True

        if has_error:
            return render_template('update_book.html', book=book, 
                                 form_data=request.form, 
                                 user=current_user.username)
        
        db.session.commit()
        flash(f'Success! "{book.title}" has been updated.', 'success')  # <-- Specific success message
        return redirect(url_for('Novel_inventory.inventory'))

    return render_template('update_book.html', book=book, 
                         form_data=None, 
                         user=current_user.username)

# Route to delete a book
@Novel_inventory.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    # Ensure only managers can delete books
    if current_user.role != "manager":
        flash("You do not have permission to delete books.", "danger")
        return redirect(url_for('Novel_inventory.inventory'))

    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('Novel_inventory.inventory'))

