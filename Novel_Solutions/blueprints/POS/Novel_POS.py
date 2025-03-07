from flask import render_template, Blueprint, redirect, url_for, request, flash, jsonify
from extensions import db
from flask_login import login_required, current_user
from models import Transaction, User
import stripe
import os
from datetime import datetime
from ..cart.Novel_cart import get_cart_total


Novel_POS = Blueprint('Novel_POS', __name__, template_folder='templates')

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


# Process Sale Route (Restricted to Cashiers)
@Novel_POS.route('/process_sale')
@login_required
def process_sale():
    if current_user.role != 'cashier':
        flash('Unauthorized! Only cashiers can process sales.', 'danger')
        return redirect(url_for('Novel_login.dashboard'))
    return render_template('process_sale.html', user=current_user)


# ✅ Route to render the checkout page (Generates PaymentIntent)
@Novel_POS.route("/checkout")
def checkout():
    try:
        subtotal, tax_amount, total_amount = get_cart_total()

        amount = int(total_amount * 100)  # Convert to cents
    
        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"]
        )

        return render_template("payment.html", 
                               stripe_publishable_key=stripe_publishable_key, 
                               client_secret=intent.client_secret, 
                               subtotal=subtotal, 
                               tax_amount=tax_amount, 
                               total_amount=total_amount)
    except Exception as e:
        return jsonify(error=str(e)), 400


# ✅ Route to create a PaymentIntent (Used by payment.html)
@Novel_POS.route("/create-payment-intent", methods=["POST"])
def create_payment():
    try:
        data = request.json
        amount = data.get("amount")  # Amount in cents

        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"]
        )

        return jsonify({"clientSecret": intent.client_secret})
    
    except Exception as e:
        return jsonify(error=str(e)), 400


# ✅ Order Confirmation Page Route
@Novel_POS.route("/order-confirmation")
def order_confirmation():
    return render_template("order_confirmation.html")


# ✅ Stripe Webhook for Payment Updates (Saves Transactions)
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

        # Save successful transaction to database
        transaction = Transaction(
            user_id=user_id,
            amount=amount_received,
            status="completed",
            stripe_payment_id=stripe_payment_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(transaction)
        db.session.commit()

        print(f"💰 Payment succeeded! PaymentIntent ID: {intent['id']} - Saved to DB")

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        stripe_payment_id = intent["id"]

        # Save failed transaction
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


# ✅ API to Fetch All Transactions (Managers & Cashiers)
@Novel_POS.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    if current_user.role not in ["manager", "cashier"]:
        return jsonify({"error": "Unauthorized"}), 403  # Restrict access
    
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    transaction_list = [
        {
            "id": t.id,
            "user": t.user_id,
            "amount": t.amount / 100,  # Convert from cents to dollars
            "status": t.status,
            "stripe_payment_id": t.stripe_payment_id,
            "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for t in transactions
    ]
    
    return jsonify(transaction_list), 200


# ✅ API to View Transactions Page
@Novel_POS.route("/transactions/view")
@login_required
def view_transactions():
    return render_template("transaction_dashboard.html")
