from flask import Blueprint, render_template, session, request, jsonify
from models import db, Book
from flask_login import current_user

# Create the Blueprint
Novel_cart = Blueprint("Novel_cart", __name__)

# Define North Carolina sales tax rate (Cary, NC - 7.25%)
NC_TAX_RATE = 0.0725


def initialize_cart():
    """Ensure the cart exists in the session."""
    if "cart" not in session:
        session["cart"] = {}


@Novel_cart.route("/cart")
def view_cart():
    """Display the cart with tax calculations."""
    initialize_cart()
    cart_items = []
    subtotal = 0
    book = Book.query.all()

    # Get discount percentage (stored in session)
    discount_percentage = session.get("discount", 0)

    for book_id, quantity in session["cart"].items():
        book = Book.query.get(int(book_id))
        if book:
            item_total = book.price * quantity
            subtotal += item_total
            cart_items.append(
                {
                    "cover": book.thumbnail_url,
                    "id": book.id,
                    "title": book.title,
                    "author": book.authors,
                    "price": book.price,
                    "quantity": quantity,
                    "total": item_total,
                }
            )

    # Calculate discount amount
    discount_amount = round((subtotal * discount_percentage) / 100, 2)
    discounted_subtotal = subtotal - discount_amount


    tax_amount = round(discounted_subtotal * NC_TAX_RATE, 2)
    total_price = round(discounted_subtotal + tax_amount, 2)

    promo_code = session.get("promo_code", None)
    return render_template(
        "cart.html",
        cart_items=cart_items,
        subtotal=subtotal,
        discount_percentage=discount_percentage,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total_price=total_price,
        user=current_user,
        promo_code=promo_code,
        book=book
    )


@Novel_cart.route("/add_to_cart/<int:book_id>", methods=["POST"])
def add_to_cart(book_id):
    """Add a book to the cart."""
    initialize_cart()
    book_id_str = str(book_id)

    if book_id_str in session["cart"]:
        session["cart"][book_id_str] += 1
    else:
        session["cart"][book_id_str] = 1

    session.modified = True
    return jsonify({"message": "Book added to cart.", "success": True})


@Novel_cart.route("/remove_from_cart/<int:book_id>", methods=["POST"])
def remove_from_cart(book_id):
    """Remove a book from the cart."""
    initialize_cart()
    book_id_str = str(book_id)

    if book_id_str in session["cart"]:
        session["cart"][book_id_str] -= 1
        if session["cart"][book_id_str] <= 0:
            del session["cart"][book_id_str]
        session.modified = True
        return jsonify({"message": "Book removed from cart.", "success": True})

    return jsonify({"message": "Item not found in cart.", "success": False})


@Novel_cart.route("/clear_cart", methods=["POST"])
def clear_cart():
    """Clear the cart."""
    session.pop("cart", None)
    session.modified = True
    return jsonify({"message": "Cart cleared.", "success": True})


def get_cart_total():
    """Calculate and return the subtotal, tax, and total amount of the cart."""
    initialize_cart()
    subtotal = 0

    for book_id, quantity in session["cart"].items():
        book = db.session.get(Book, int(book_id))
        if book:
            subtotal += book.price * quantity


    # Retrieve discount percentage
    discount_percentage = session.get("discount", 0)
    discount_amount = round((subtotal * discount_percentage) / 100, 2)
    discounted_subtotal = subtotal - discount_amount

    tax_amount = round(discounted_subtotal * NC_TAX_RATE, 2)
    total_price = round(discounted_subtotal + tax_amount, 2)  # Total with tax
    return subtotal, tax_amount, total_price, discount_amount

# Apply discount via promo code
@Novel_cart.route("/apply_discount", methods=["POST"])
def apply_discount():
    data = request.get_json()
    promo_code = data.get("promo_code", "").strip().upper()  # Normalize input
    discounts = {
        "SAVE10": 10,  # 10% discount
        "BOOKS25": 25,  # 25% discount
        "FREESHIP": 5,  # 5% discount
        "NOVEL50": 50,  # 50% discount
        "FLASH20": 20,  # 20% discount
        "WELCOME15": 15,  # 15% discount
    }

    current_code = session.get("promo_code")
    current_discount = session.get("discount", 0)

    # Prevent applying the same code again
    if current_code == promo_code:
        return jsonify({
            "message": "That discount has already been applied. Please remove it before applying a new one.",
            "discount": current_discount
        }), 400

    # Prevent stacking multiple discounts
    if current_discount > 0:
        return jsonify({
            "message": f"A {current_discount}% discount is already applied. Please remove it before applying a new one.",
            "discount": current_discount
        }), 400

    # Apply valid discount
    if promo_code in discounts:
        session["discount"] = discounts[promo_code]
        session["promo_code"] = promo_code
        return jsonify({
            "message": f"{discounts[promo_code]}% discount applied!",
            "discount": discounts[promo_code]
        })

    # Handle invalid code
    return jsonify({
        "message": "Invalid promo code!",
        "discount": 0
    }), 400

@Novel_cart.route("/remove_discount", methods=["POST"])
def remove_discount():
    """Remove any applied discount."""
    discount_removed = False

    if "discount" in session:
        session.pop("discount")
        discount_removed = True

    if "promo_code" in session:
        session.pop("promo_code")
        discount_removed = True

    session.modified = True

    if discount_removed:
        return jsonify({"message": "Discount removed!", "discount": 0})
    else:
        return jsonify({"message": "No discount applied!", "discount": 0}), 400
