from flask import Flask, render_template, Blueprint

# Create a Blueprint object
Novel_login = Blueprint('login', __name__, template_folder='templates')



# basic home route to get started 
@Novel_login.route('/', methods=['GET'])
def home():
    return render_template('login.html')