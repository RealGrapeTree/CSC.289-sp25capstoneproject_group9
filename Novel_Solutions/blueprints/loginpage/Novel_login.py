
# Imports the required libraries
from flask import  render_template, Blueprint, redirect, url_for, request, flash, current_app
from extensions import db, bcrypt, login_manager

# Imports for Login
from flask_login import login_user, logout_user, current_user, login_required

# Imports for the Forms
from .User_forms import RegisterForm, LoginForm

# Imports for the Models
from models import User

# Create a Blueprint object 
Novel_login = Blueprint('Novel_login', __name__, template_folder='templates')

# Set up flask-login
login_manager.login_view = "Novel_login.login"


# Create a UserLoader for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


#basic home route can move to a home or iventory blueprint if needed
@Novel_login.route('/', methods=['POST','GET'])
def home():
    return render_template('home.html')

# login page route
@Novel_login.route('/login', methods=['POST','GET'])
def login():
    
    # check if the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('Novel_login.dashboard'))
    form = LoginForm()

    if form.validate_on_submit():
        # query the database for the user
        user = User.query.filter_by(username=form.username.data).first()

        # check if the user exists and the password is correct
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                # Log in the user after successful login
                login_user(user)
                # flash a success message and redirect to dashboard
                flash('Login successful!', 'success')
                return redirect(url_for('Novel_login.dashboard'))
        else:   
            # flash an error message and redirect to the login page
            flash('Login unsuccessful. Please check username and password', 'danger')
            return redirect(url_for('Novel_login.login'))   
        
    return render_template('login.html', form=form)
    

@Novel_login.route('/logout', methods=['POST','GET'])
@login_required
def logout():
    # logout the user
    logout_user()
    flash('You have been logged out')
    # redirect to the login page
    return redirect(url_for('Novel_login.login'))

# register page route
@Novel_login.route('/add_user', methods=['POST','GET'])
def add_user():
    
    if not current_user.is_authenticated or current_user.role != 'manager':
        flash('Unauthorized! Only managers can add users.', 'danger')
        return redirect(url_for('Novel_login.dashboard'))
    
    # create a new instance of the registration form
    form = RegisterForm()

    if form.validate_on_submit():
        
        # hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # create a new user object
        user = User(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password, role=form.role.data)

        # add the new user to the database
        db.session.add(user)
        # commit the changes
        db.session.commit()

        # flash a success message and redirect to the login page
        flash('User created successfully!', 'success')
        
        return redirect(url_for('Novel_login.dashboard'))

    return render_template('add_user.html', form=form)


# Delete User Route
@Novel_login.route('/delete_user/<string:username>', methods=['POST'])
@login_required
def delete_user(username):
    if current_user.role != 'manager':
        flash('Unauthorized! Only managers can delete users.', 'danger')
        return redirect(url_for('Novel_login.dashboard'))

    user = User.query.get(username)  # Lookup by username (Primary Key)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found!', 'danger')

    return redirect(url_for('Novel_login.dashboard'))

# Dashboard route
@Novel_login.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all() if current_user.is_authenticated and current_user.role == 'manager' else None
    return render_template('dashboard.html', user=current_user, users=users)


