from flask import Flask, render_template, Blueprint, redirect

# Create a Blueprint object
Novel_login = Blueprint('login', __name__, template_folder='templates')



#basic home route can move to a home blueprint if needed
@Novel_login.route('/', methods=['GET'])
def home():
    return render_template('base.html')


# login page route
@Novel_login.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# register page route
@Novel_login.route('/register', methods=['GET'])
def register():
    return render_template('register.html')



