
from flask import  render_template, Blueprint, redirect, url_for, request, flash, jsonify
from extensions import db, bcrypt, login_manager
from flask_login import  UserMixin, login_user, logout_user, current_user, login_required
from ..loginpage.Novel_login import Novel_login
import stripe 
import os

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




# ✅ Route to render the checkout page (Now generates PaymentIntent)
@Novel_POS.route("/checkout")
def checkout():
    try:
        amount = 5000  # Example: $50.00 (Stripe processes amounts in cents)
    
        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"]
        )

        return render_template("payment.html", 
                               stripe_publishable_key=stripe_publishable_key, 
                               client_secret=intent.client_secret)
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
    return render_template("order_confirmation.html")  # Redirects to a confirmation page

# ✅ Stripe Webhook for Payment Updates
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
        print(f"💰 Payment succeeded! PaymentIntent ID: {intent['id']}")
    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        print(f"❌ Payment failed. PaymentIntent ID: {intent['id']}")

    return jsonify({"status": "success"}), 200