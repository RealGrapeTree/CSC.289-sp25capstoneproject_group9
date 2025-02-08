#import flask module
from flask import Flask
from dotenv import load_dotenv
from blueprints.loginpage.Novel_login import Novel_login
from .extensions import db

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




# registers the Novel login blueprint to the app 
app.register_blueprint(Novel_login)



if __name__ == "__main__":
    app.run(debug=True)