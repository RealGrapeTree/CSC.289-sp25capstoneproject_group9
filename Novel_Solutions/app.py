#import flask module
from flask import Flask
from dotenv import load_dotenv
from blueprints.loginpage.Novel_login import Novel_login

# import os module to access environment variables
import os

#load the environment variables from the .env file
load_dotenv()

# Create an instance of the Flask application
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

app.register_blueprint(Novel_login)



if __name__ == "__main__":
    app.run(debug=True)