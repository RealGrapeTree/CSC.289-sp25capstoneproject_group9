#import flask module
from flask import Flask

from dotenv import load_dotenv
from blueprints.loginpage.Novel_login import Novel_login
from blueprints.POS.Novel_POS import Novel_POS
from extensions import db, bcrypt, login_manager
from models import User

# import os module to access environment variables
import os

#load the environment variables from the .env file
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

# registers the Novel login blueprint to the app 
app.register_blueprint(Novel_login)

# registers the Novel POS blueprint to the app
app.register_blueprint(Novel_POS)

def create_default_manager():
    with app.app_context():  # Ensure the Flask app context is active
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            manager = User(username="admin", firstname="Admin", lastname="User", email="admin@example.com", password=hashed_password, role="manager")
            db.session.add(manager)
            db.session.commit()
            print("Default manager account created: admin/admin123")



# maybe move this  
create_default_manager()


if __name__ == "__main__":
    
    app.run(debug=True)