from flask import render_template, Blueprint, redirect, url_for, request, flash, jsonify, session
from extensions import db
from flask_login import login_required, current_user
from models import Transaction, User, Book, TransactionItem
import stripe
import os
from datetime import datetime
from ..cart.Novel_cart import get_cart_total
import random

Novel_POS = Blueprint('Novel_POS', __name__, template_folder='templates')

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


def save_transaction_to_db(user_id, amount, status, stripe_payment_id, cart):
    print("Saving transaction to DB...")
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        status=status,
        stripe_payment_id=stripe_payment_id,
        timestamp=datetime.now()
    )
    db.session.add(transaction)
    db.session.commit()
    
    # Save each cart item in the TransactionItem table
    for book_id, quantity in cart.items():
        print(f"Processing book ID: {book_id} with quantity: {quantity}")
        
        book = db.session.get(Book, int(book_id))
        
        if book is None:
            print(f"❌ Book not found for ID: {book_id}")
            continue  # Skip this book if not found
        
        print(f"Processing book: {book.title} (ISBN: {book.isbn}) with quantity: {quantity}")
        
        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            book_id=book.id,
            quantity=quantity,
            unit_price=int(book.price * 100),  # Store unit price in cents
            isbn=book.isbn,
            book_title=book.title  # Store the title for reference
        )
        db.session.add(transaction_item)

    db.session.commit()
    print("Transaction saved successfully!")



# ✅ Route to render the checkout page (Generates PaymentIntent)
@Novel_POS.route("/checkout")
def checkout():
    try:
        cart = session.get('cart', {})
        is_valid, error_message = validate_stock_before_payment(cart)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('Novel_cart.view_cart'))
        totals = get_cart_total()
        subtotal, tax_amount, total_amount = totals[:3]
        extra_values = totals[3:]  # Optional

        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),
            currency="usd",
            payment_method_types=["card"]
        )

        return render_template("payment.html",
                               user=current_user,
                               stripe_publishable_key=stripe_publishable_key,
                               client_secret=intent.client_secret,
                               subtotal=subtotal,
                               tax_amount=tax_amount,
                               total_amount=total_amount,
                               extra_values=extra_values)

    except Exception as e:
        return jsonify(error=str(e)), 400


def validate_stock_before_payment(cart):
    for book_id, quantity in cart.items():
        book = Book.query.get(int(book_id))
        if book and book.stock < quantity:
            return False, f"Not enough stock for {book.title}. Only {book.stock} available."
    return True, None


def update_inventory_after_sale(cart):
    try:
        for book_id, quantity in cart.items():
            book = db.session.get(Book, int(book_id))
            if book:
                book.stock -= quantity
                if book.stock < 0:
                    book.stock = 0
                db.session.add(book)

        db.session.commit()
        print("✅ Inventory updated successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating inventory: {e}")


# ✅ Route to select payment method
@Novel_POS.route("/select-payment", methods=["GET"])
def select_payment():
    try:
        cart = session.get('cart', {})
        totals = get_cart_total()
        subtotal, tax_amount, total_amount = totals[:3]
        return render_template("select_payment.html", 
                               user=current_user,
                               total_amount=total_amount)
    except Exception as e:
        return jsonify(error=str(e)), 400

# ✅ Route for Cash checkout
@Novel_POS.route("/cash_checkout", methods=["GET"])
def cash_checkout():
    try:
        cart = session.get('cart', {})
        subtotal, tax_amount, total_amount = get_cart_total()[:3] 
        save_transaction_to_db(current_user.username, total_amount, "Cash Payment", f"Cash Payment {random.randint(0, 999999)}", cart)
        return render_template('cash_checkout.html', 
                               user=current_user, 
                               subtotal=subtotal,
                               tax_amount=tax_amount,
                               total_amount=total_amount)
    except Exception as e:
        return jsonify(error=str(e)), 400

# ✅ Route to create a PaymentIntent
@Novel_POS.route("/create-payment-intent", methods=["POST"])
def create_payment():
    try:
        data = request.json
        amount = data.get("amount")

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"]
        )

        cart = session.get('cart', {})
        update_inventory_after_sale(cart)  # Call the new function

       # Save transaction to the database
        save_transaction_to_db(current_user.username, amount, "completed", intent.id, cart)

        # Clear the cart after payment
        session['cart'] = {}
        session.modified = True

        return jsonify({"clientSecret": intent.client_secret})
    except Exception as e:
        return jsonify(error=str(e)), 400


# ✅ Order Confirmation Page
@Novel_POS.route("/order-confirmation")
def order_confirmation():
    return render_template("order_confirmation.html")


# ✅ Stripe Webhook
@Novel_POS.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, stripe_webhook_secret)
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        amount_received = intent["amount_received"]
        stripe_payment_id = intent["id"]
        user_id = current_user.username if current_user.is_authenticated else "unknown"

        

        print(f"💰 Payment succeeded! PaymentIntent ID: {intent['id']}")

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        stripe_payment_id = intent["id"]

        transaction = Transaction(
            user_id="unknown",
            amount=intent["amount"],
            status="failed",
            stripe_payment_id=stripe_payment_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(transaction)
        db.session.commit()
        print(f"❌ Payment failed. PaymentIntent ID: {intent['id']} - Logged in DB")

    return jsonify({"status": "success"}), 200


# ✅ View All Transactions API
@Novel_POS.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    if current_user.role not in ["manager", "cashier"]:
        return jsonify({"error": "Unauthorized"}), 403

    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    transaction_list = [
        {
            "id": t.id,
            "user": t.user_id,
            "amount": t.amount / 100,
            "status": t.status,
            "stripe_payment_id": t.stripe_payment_id,
            "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for t in transactions
    ]

    return jsonify(transaction_list), 200


# ✅ View Transactions Page
@Novel_POS.route("/transactions/view")
@login_required
def view_transactions():
    return render_template("transaction_dashboard.html")


# ✅ Refund Route
@Novel_POS.route("/refund/<int:transaction_id>", methods=["POST"])
@login_required
def refund(transaction_id):
    if current_user.role not in ["manager", "cashier"]:
        flash('Unauthorized! Only cashiers or managers can issue refunds.', 'danger')
        return redirect(url_for('Novel_POS.view_transactions'))

    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.status == "refunded":
        flash('This transaction has already been refunded.', 'danger')
        return redirect(url_for('Novel_POS.view_transactions'))

    if transaction.status != "completed":
        flash('Only completed transactions can be refunded.', 'danger')
        return redirect(url_for('Novel_POS.view_transactions'))

    try:
        refund = stripe.refunds.create(
            payment_intent=transaction.stripe_payment_id
        )
        transaction.status = "refunded"
        db.session.commit()

        flash('Refund processed successfully!', 'success')
    except stripe.error.StripeError as e:
        flash(f'Error processing refund: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'danger')

    return redirect(url_for('Novel_POS.view_transactions'))


# ✅ Email Receipt Route
@Novel_POS.route('/send-receipt/email', methods=["POST"])
def send_email_receipt():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"message": "❌ Please provide a valid email."}), 400

    try:
        print(f"📧 Sending receipt to {email}...")  # Replace with Flask-Mail later
        return jsonify({"message": f"✅ Receipt sent to {email}!"}), 200
    except Exception as e:
        return jsonify({"message": f"❌ Error sending email: {str(e)}"}), 500


# ✅ SMS Receipt Route
@Novel_POS.route('/send-receipt/sms', methods=["POST"])
def send_sms_receipt():
    data = request.get_json()
    phone = data.get("phone")

    if not phone:
        return jsonify({"message": "❌ Please provide a valid phone number."}), 400

    try:
        print(f"📱 Sending SMS receipt to {phone}...")  # Replace with Twilio later
        return jsonify({"message": f"✅ Receipt sent via SMS to {phone}!"}), 200
    except Exception as e:
        return jsonify({"message": f"❌ Error sending SMS: {str(e)}"}), 500
