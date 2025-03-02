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



def backup_database():
    """Creates a backup of the SQLite database.

    The backup is saved in the 'backups' directory with a filename in the format
    'backup_<timestamp>.db', where <timestamp> is the current date and time in
    the format '%Y%m%d%H%M%S'.
    """
    
    backup_dir = 'instance'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.db')
    shutil.copy('instance/database.db', backup_file) 
    print(f"Database backup created: {backup_file}")


def backup_schedule(interval = 3600): # 1 hour
    # runs database backup at startup
    """Runs the database backup at startup and then every <interval> seconds.

    :param interval: The interval in seconds between backups. Defaults to 1 hour.
    """
    backup_database()

    while True:
        time.sleep(interval)
        backup_database()
    

backup_thread =threading.Thread(target=backup_schedule, daemon=True)
backup_thread.start()


if __name__ == "__main__":
   
    app.run(debug=True)
