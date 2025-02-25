# Import necessary modules
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from blueprints.loginpage.Novel_login import Novel_login
from blueprints.POS.Novel_POS import Novel_POS
from blueprints.inventory.Novel_inventory import Novel_inventory
from blueprints.cart.Novel_cart import Novel_cart
from extensions import db, bcrypt, login_manager
from models import User, Book
import os
import stripe

# Load the environment variables from the .env file
load_dotenv()

# Create an instance of the Flask application
app = Flask(__name__)

# Set the secret key to the SECRET_KEY environment variable
app.secret_key = os.getenv('SECRET_KEY')

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

# Create the database tables
with app.app_context():
    db.create_all()

# Configure the Bcrypt module
bcrypt.init_app(app)

# Configure the LoginManager
login_manager.init_app(app)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

# Register blueprints
app.register_blueprint(Novel_login)
app.register_blueprint(Novel_POS)
app.register_blueprint(Novel_inventory)
app.register_blueprint(Novel_cart)

# Function to create the default manager account if it doesn't exist
def create_default_manager():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            manager = User(username="admin", firstname="Admin", lastname="User", 
                           email="admin@example.com", password=hashed_password, role="manager")
            db.session.add(manager)
            db.session.commit()
            print("Default manager account created: admin/admin123")

# Create the default admin account
create_default_manager()

# ✅ Route to render the checkout page (Now generates PaymentIntent)
@app.route("/checkout")
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
@app.route("/create-payment-intent", methods=["POST"])
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
@app.route("/order-confirmation")
def order_confirmation():
    return render_template("order_confirmation.html")  # Redirects to a confirmation page

# ✅ Stripe Webhook for Payment Updates
@app.route("/webhook", methods=["POST"])
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

if __name__ == "__main__":
    app.run(debug=True)
