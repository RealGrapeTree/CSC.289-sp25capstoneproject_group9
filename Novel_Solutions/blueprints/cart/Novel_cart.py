from flask import Blueprint, render_template, session, request, jsonify
from models import db, Book

# Create the Blueprint
Novel_cart = Blueprint('Novel_cart', __name__)

# Define North Carolina sales tax rate (Cary, NC - 7.25%)
NC_TAX_RATE = 0.0725

def initialize_cart():
    """Ensure the cart exists in the session."""
    if 'cart' not in session:
        session['cart'] = {}

@Novel_cart.route('/cart')
def view_cart():
    """Display the cart with tax calculations."""
    initialize_cart()
    cart_items = []
    subtotal = 0

    for book_id, quantity in session['cart'].items():
        book = Book.query.get(int(book_id))
        if book:
            item_total = book.price * quantity
            subtotal += item_total
            cart_items.append({
                'id': book.id,
                'title': book.title,
                'price': book.price,
                'quantity': quantity,
                'total': item_total
            })

    tax_amount = round(subtotal * NC_TAX_RATE, 2)
    total_price = round(subtotal + tax_amount, 2)

    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal, tax_amount=tax_amount, total_price=total_price)

@Novel_cart.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    """Add a book to the cart."""
    initialize_cart()
    book_id_str = str(book_id)

    if book_id_str in session['cart']:
        session['cart'][book_id_str] += 1
    else:
        session['cart'][book_id_str] = 1

    session.modified = True
    return jsonify({'message': 'Book added to cart', 'success': True})

@Novel_cart.route('/remove_from_cart/<int:book_id>', methods=['POST'])
def remove_from_cart(book_id):
    """Remove a book from the cart."""
    initialize_cart()
    book_id_str = str(book_id)

    if book_id_str in session['cart']:
        session['cart'][book_id_str] -= 1
        if session['cart'][book_id_str] <= 0:
            del session['cart'][book_id_str]
        session.modified = True
        return jsonify({'message': 'Book removed from cart', 'success': True})

    return jsonify({'message': 'Item not found in cart', 'success': False})

@Novel_cart.route('/clear_cart', methods=['POST'])
def clear_cart():
    """Clear the cart."""
    session.pop('cart', None)
    session.modified = True
    return jsonify({'message': 'Cart cleared', 'success': True})
