# Imports for the Flask Framework
from flask import flash

# Imports for the Forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError

# Imports for the Models
from models import User



# User Registration Form class
class RegisterForm(FlaskForm):
    username = StringField("Enter Username", validators=[InputRequired(), Length(min=4, max=20)]) 
    firstname = StringField("Enter First Name", validators=[InputRequired(), Length(min=2, max=30)])
    lastname = StringField("Enter Last Name", validators=[InputRequired(), Length(min=2, max=30)])
    password = PasswordField("Enter Password", validators=[InputRequired(), Length(min=8, max=20)]) 
    email = EmailField("Enter Email", validators=[InputRequired(), Length(max=254)]) 
    role = SelectField('Role', choices=[('manager', 'Manager'), ('cashier', 'Cashier')])

    submit = SubmitField("Add User")

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
