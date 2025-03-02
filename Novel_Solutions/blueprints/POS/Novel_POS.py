from flask import render_template, Blueprint, redirect, url_for, request, flash, jsonify
from extensions import db, bcrypt, login_manager
from flask_login import UserMixin, login_user, logout_user, current_user, login_required
from ..loginpage.Novel_login import Novel_login
from ..cart.Novel_cart import Novel_cart, get_cart_total  # Import cart total function
import stripe
import os
from models import Transaction, InventoryTransaction, Inventory, RefundRequest

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


# Route to render the checkout page (Now generates PaymentIntent)
@Novel_POS.route("/checkout")
def checkout():
    try:
        subtotal, tax_amount, total_amount = get_cart_total()

        amount = int(total_amount * 100)

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


# Route to create a PaymentIntent (Used by payment.html)
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


# Order Confirmation Page Route
@Novel_POS.route("/order-confirmation")
def order_confirmation():
    return render_template("order_confirmation.html")  # Redirects to a confirmation page


# Stripe Webhook for Payment Updates
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
        # Optionally, update the transaction in your database
    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        print(f"❌ Payment failed. PaymentIntent ID: {intent['id']}")
    elif event["type"] == "payment_intent.refunded":
        intent = event["data"]["object"]
        print(f"💸 Payment refunded! PaymentIntent ID: {intent['id']}")
        # Optionally, mark the transaction as refunded in your database
        transaction = Transaction.query.filter_by(stripe_payment_id=intent['id']).first()
        if transaction:
            transaction.status = 'refunded'
            transaction.refunded = True
            db.session.commit()

    return jsonify({"status": "success"}), 200


# Refund Route (Restricted to Admins or Cashiers)
@Novel_POS.route('/refund/<int:transaction_id>', methods=["POST"])
@login_required
def refund(transaction_id):
    if current_user.role not in ['cashier', 'manager']:  # Only allow cashiers or managers to refund
        flash('Unauthorized! Only cashiers or managers can process refunds.', 'danger')
        return redirect(url_for('Novel_login.dashboard'))

    # Retrieve the transaction from the database
    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.status != 'completed':
        flash('Refund can only be processed for completed transactions.', 'danger')
        return redirect(url_for('Novel_POS.order_confirmation'))

    if transaction.refunded:
        flash('This transaction has already been refunded.', 'warning')
        return redirect(url_for('Novel_POS.order_confirmation'))

    # Process refund via Stripe
    try:
        # Refund the payment using the payment_intent_id from Stripe
        refund = stripe.Refund.create(
            payment_intent=transaction.stripe_payment_id  # Use the PaymentIntent ID saved in the transaction
        )

        # Mark the transaction as refunded in the database
        transaction.refunded = True
        transaction.status = 'refunded'
        db.session.commit()

        # Adjust inventory based on refunded items (this assumes you have an InventoryTransaction model)
        inventory_transactions = InventoryTransaction.query.filter_by(transaction_id=transaction.id).all()
        for inv_transaction in inventory_transactions:
            if inv_transaction.change_type == 'sale':  # Adjust stock based on sale records
                inventory = Inventory.query.filter_by(book_id=inv_transaction.book_id).first()
                if inventory:
                    inventory.stock += inv_transaction.quantity  # Increase stock based on the quantity refunded
                    db.session.commit()

        flash('Refund successfully processed!', 'success')
        return redirect(url_for('Novel_POS.order_confirmation'))

    except stripe.error.StripeError as e:
        flash(f"Refund failed: {e.user_message}", 'danger')
        return redirect(url_for('Novel_POS.order_confirmation'))
    

@Novel_POS.route('/previous_orders')
@login_required
def previous_orders():
    orders = Transaction.query.filter_by(user_id=current_user.username).all()

    return render_template('previous_orders.html', orders=orders, user=current_user)   


# Route to request a refund
@Novel_POS.route('/request_refund/<int:order_id>', methods=['GET', 'POST'])
@login_required
def request_refund(order_id):
    order = Transaction.query.get_or_404(order_id)

    if order.user_id != current_user.username:  # Make sure user_id is the same as current user's username
        flash('You can only request a refund for your own orders.', 'danger')
        return redirect(url_for('Novel_POS.previous_orders'))

    if order.status != 'completed':
        flash('Only completed orders can be refunded.', 'danger')
        return redirect(url_for('Novel_POS.previous_orders'))

    if order.refunded:
        flash('This order has already been refunded.', 'warning')
        return redirect(url_for('Novel_POS.previous_orders'))

    if request.method == 'POST':
        reason = request.form['reason']
        refund_request = RefundRequest(
            order_id=order.id,
            user_id=current_user.username,  # Use username as user_id
            reason=reason,
            status='pending'  # Initially, the request status is 'pending'
        )
        db.session.add(refund_request)
        db.session.commit()
        
        flash('Your refund request has been submitted. Awaiting manager approval.', 'success')
        return redirect(url_for('Novel_POS.previous_orders'))

    return render_template('request_refund.html', order=order)


# Manager Dashboard to view pending refund requests
@Novel_POS.route('/manager/refund_requests')
@login_required
def manager_refund_requests():
    if current_user.role != 'manager':
        flash('Unauthorized! Only managers can view refund requests.', 'danger')
        return redirect(url_for('Novel_login.dashboard'))

    # Retrieve all pending refund requests
    refund_requests = RefundRequest.query.filter_by(status='pending').all()

    return render_template('manager_refund_requests.html', refund_requests=refund_requests)


# Manager's action to approve or deny refund requests
@Novel_POS.route('/manager/manage_refund/<int:refund_id>', methods=["POST"])
@login_required
def manage_refund(refund_id):
    if current_user.role != 'manager':
        flash('Unauthorized! Only managers can manage refund requests.', 'danger')
        return redirect(url_for('Novel_login.dashboard'))

    refund_request = RefundRequest.query.get_or_404(refund_id)

    action = request.form.get('action')

    if action == 'accept':
        refund_request.status = 'accepted'
        # Optionally, process the refund with Stripe here if needed
        flash('Refund request accepted and processed.', 'success')

    elif action == 'deny':
        refund_request.status = 'denied'
        flash('Refund request denied.', 'danger')

    db.session.commit()

    return redirect(url_for('Novel_POS.manager_refund_requests'))