# Import necessary modules
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
from flask_login import LoginManager, login_required, current_user,logout_user
from blueprints.loginpage.Novel_login import Novel_login, logout, current_user
from blueprints.POS.Novel_POS import Novel_POS
from blueprints.inventory.Novel_inventory import Novel_inventory
from blueprints.cart.Novel_cart import Novel_cart, get_cart_total  # Import cart total function
from extensions import db, bcrypt, login_manager
from models import User, Book
import shutil
from datetime import datetime
import threading
import time
import os
import stripe





# Load the environment variables from the .env file
load_dotenv()

# Create an instance of the Flask application
app = Flask(__name__)

# Set the secret key to the SECRET_KEY environment variable
app.secret_key = os.getenv('SECRET_KEY')

app.config['SESSION_PERMANENT'] = False

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

# Configure Stripe API with secret key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

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

# Route to fetch Stripe transactions
@app.route('/api/inventory/stripe-transactions', methods=['GET'])
def fetch_transactions():
    try:
        # Fetch recent transactions (charges) from Stripe
        charges = stripe.Charge.list(limit=10)  # Adjust the limit as needed

        # Format transactions for display
        transactions = []
        for charge in charges.auto_paging_iter():
            transactions.append({
                'id': charge.id,
                'amount': charge.amount,
                'status': charge.status,
                'stripe_payment_id': charge.payment_intent,
                'timestamp': charge.created  # UNIX timestamp
            })
        
        return jsonify(transactions), 200  # Return as JSON response

    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 500  # Return error if Stripe API fails


if __name__ == "__main__":
   
    app.run(debug=True)
