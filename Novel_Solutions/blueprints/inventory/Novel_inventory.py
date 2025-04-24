from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for,abort
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
        number_of_pages = book_info.get('number_of_pages', None)
        publishers = ', '.join([publisher['name'] for publisher in book_info.get('publishers', [])])
        publish_date = book_info.get('publish_date', 'Unknown')
        thumbnail_url = book_info.get('cover', {}).get('medium', 'Unknown')
        cover = book_info.get('cover', {}).get('large', 'Unknown')

        return isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover
    return None, None, None, None, None, None, None, None


# Use this function in a Show All Inventory page

# Function to check all books in the database
def check_books():
    books = Book.query.all()
    for book in books:
        print(f"ID: {book.id}, ISBN: {book.isbn}, SKU: {book.sku}, Title: {book.title}, Stock: {book.stock}, Price: ${book.price:.2f}")


@Novel_inventory.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    # Check if the user is logged in
    if current_user.is_authenticated:
        # Get the search term from the form
        if request.method == 'POST':

            # Check if this is a manual add request
            if 'manual_add' in request.form:
                # Handle manual book addition
                if current_user.role != "manager":
                    flash('Only managers can add books manually.', 'danger')
                    return redirect(url_for('Novel_inventory.add_book'))
                
                # Create form_data from the submitted form
                form_data = {
                    'isbn': request.form.get('isbn'),
                    'title': request.form.get('title'),
                    'authors': request.form.get('authors'),
                    'number_of_pages': request.form.get('number_of_pages'),
                    'publishers': request.form.get('publishers'),
                    'publish_date': request.form.get('publish_date'),
                    'thumbnail_url': request.form.get('thumbnail_url', ''),
                    'cover': request.form.get('cover', ''),
                    'stock': request.form.get('stock', 10),
                    'price': request.form.get('price', 19.99)
                }
                
                if not form_data['title'] or not form_data['authors']:
                    flash('Title and Author(s) are required fields.', 'danger')
                    return render_template('add_book.html',
                                       not_found=True,
                                       form_data=form_data,
                                       user=current_user)
                try:
                    new_book = insert_book_into_db(**form_data)
                    flash('Book added to inventory.', 'success')
                    return render_template('add_book.html', book=new_book, user=current_user)
                except Exception as e:
                    flash(f'Error adding book: {str(e)}', 'danger')
                    return render_template('add_book.html',
                                         not_found=True,
                                         form_data=form_data,
                                         user=current_user)
            search_term = request.form['search_term']
            stock = request.form['stock']
            price = request.form['price']
            book = Book.query.filter((Book.isbn == search_term) | (Book.sku == search_term)).first()
            
            # Check if the book exists within database
            if book:
                if book.stock == 0:
                    book.stock = int(stock)
                    book.price = float(price)
                    db.session.commit()
                    flash('Book restocked successfully.', 'success')
                else:
                    flash('Book already exists in inventory.', 'info')

                return render_template('add_book.html', book=book, user=current_user)

            # Fetch book data from Open Library API if not found within database
            else:
                # Fetch book data from Open Library API
                isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover = get_book_data(search_term)
                
                # if book was found insert into database
                # Require isbn, title, and authors to avoid inserting placeholder data
                if isbn and title and authors:
                    flash('Book added to inventory.', 'success')
                    new_book = insert_book_into_db(isbn, title, authors, number_of_pages, publishers, publish_date, thumbnail_url, cover, stock, price)


                    return render_template('add_book.html', book=new_book , user=current_user)
                

                else:
                    # Book not found - prepare form data
                    form_data = {
                        'isbn': search_term,
                        'stock': stock,
                        'price': price,
                        'title': title if title else '',
                        'authors': authors if authors else '',
                        'number_of_pages': number_of_pages if number_of_pages else '',
                        'publishers': publishers if publishers else '',
                        'publish_date': publish_date if publish_date else '',
                        'thumbnail_url': thumbnail_url if thumbnail_url else '',
                        'cover': cover if cover else ''
                    }
                    # Book not found in Open Library - show manual entry form for managers
                    if current_user.role == "manager":
                        flash('Book not found. Please enter details manually.', 'info')
                        return render_template('add_book.html', 
                                             not_found=True,
                                             form_data=form_data,
                                             user=current_user)
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
        books_pagination = Book.query.filter(Book.stock > 0)\
                                   .order_by(Book.title)\
                                    .paginate(page=page, per_page=per_page, error_out=False)
        books = books_pagination.items
        
        return render_template('inventory.html', 
                             books=books, 
                             pagination=books_pagination,
                             user=current_user)
    else:
        return redirect(url_for('Novel_login.login'))
        

# Route to search for a book by ISBN or SKU
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
    book = db.session.get(Book, book_id)
    if not book:
        abort(404)

    if current_user.role != "manager":
        flash("You do not have permission to update books.", "danger")
        return redirect(url_for('Novel_inventory.inventory'))

    if request.method == 'POST':
        book.title = request.form['title']
        book.authors = request.form['authors']
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
                                 user=current_user)
        
        db.session.commit()
        flash(f'Success! "{book.title}" has been updated.', 'success')  # <-- Specific success message
        return redirect(url_for('Novel_inventory.inventory'))

    return render_template('update_book.html', book=book, 
                         form_data=None, 
                         user=current_user)


# Route to delete a book
@Novel_inventory.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        abort(404)

    # Ensure only managers can delete books
    if current_user.role != "manager":
        flash("You do not have permission to delete books.", "danger")
        return redirect(url_for('Novel_inventory.inventory'))

    # Soft-delete by setting stock to 0
    book.stock = 0
    db.session.commit()


    flash('Book removed from inventory', 'success')
    return redirect(url_for('Novel_inventory.inventory'))
