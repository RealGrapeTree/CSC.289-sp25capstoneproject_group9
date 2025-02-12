
# Imports the required libraries
from flask import  render_template, Blueprint, redirect, url_for, request, flash
from extensions import db, bcrypt, login_manager

# Imports for Login
from flask_login import  UserMixin, login_user, logout_user, current_user, login_required

# Imports for the Forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError 

# Create a Blueprint object 
Novel_login = Blueprint('Novel_login', __name__, template_folder='templates')

# Set up flask-login
login_manager.login_view = "Novel_login.login"


# User Registration Form class
class RegisterForm(FlaskForm):
    username = StringField("Enter Username", validators=[InputRequired(), Length(min=4, max=20)]) 
    firstname = StringField("Enter First Name", validators=[InputRequired(), Length(min=2, max=30)])
    lastname = StringField("Enter Last Name", validators=[InputRequired(), Length(min=2, max=30)])
    password = PasswordField("Enter Password", validators=[InputRequired(), Length(min=8, max=20)]) 
    email = EmailField("Enter Email", validators=[InputRequired(), Length(max=254)]) 

    submit = SubmitField("Sign Up")

    # Function to validate if username already exists
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            flash('Username already exists', 'danger')
            raise ValidationError('Username already exists')
        
    # Function to validate if email already exists
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            flash('Email already exists', 'danger')
            raise ValidationError('Email already exists')

# Form for User Login
class LoginForm(FlaskForm):
    username = StringField("Enter Username", validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField("Enter Password", validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField("Login")


# Create a User model that works with Flask-Login
class User(db.Model, UserMixin):  # Inherit from UserMixin to get default implementation of required methods
    username = db.Column(db.String(20), primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def get_id(self):
        return str(self.username)


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
        return redirect(url_for('Novel_login.home'))
    form = LoginForm()

    if form.validate_on_submit():
        # query the database for the user
        user = User.query.filter_by(username=form.username.data).first()

        # check if the user exists and the password is correct
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                # Log in the user after successful login
                login_user(user)
                # flash a success message and redirect to the inventory page
                flash('Login successful!', 'success')
                return redirect(url_for('Novel_login.inventory'))
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
@Novel_login.route('/register', methods=['POST','GET'])
def register():
    # check if the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("Novel_login.inventory"))
    
    # create a new instance of the registration form
    form = RegisterForm()

    if form.validate_on_submit():
        
        # hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # create a new user object
        user = User(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)

        # add the new user to the database
        db.session.add(user)
        # commit the changes
        db.session.commit()

        # Log in the user after successful registration
        login_user(user)

        # flash a success message and redirect to the login page
        flash('Registration successful!', 'success')

        # may change to Novel_inventory.inventory  or home once the inventory blueprint is created
        return redirect(url_for('Novel_login.inventory'))

    return render_template('register.html', form=form)


# test route will move to inventory blueprint or change the login route to redirect to the inventory blueprint after it's created
@Novel_login.route('/inventory', methods=['POST','GET'])
@login_required
def inventory():
    return render_template('inventory.html', username=current_user.username)
