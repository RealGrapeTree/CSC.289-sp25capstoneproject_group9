# Imports for the Flask Framework
from flask import flash

# Imports for the Forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo

# Imports for the Models
from models import User



# User Registration Form class
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=20)]) 
    firstname = StringField("First Name", validators=[InputRequired(), Length(min=2, max=30)])
    lastname = StringField("Last Name", validators=[InputRequired(), Length(min=2, max=30)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=20)]) 
    email = EmailField("Email", validators=[InputRequired(), Length(max=254)]) 
    role = SelectField('Role', choices=[('manager', 'Manager'), ('cashier', 'Cashier')])

    submit = SubmitField("Submit")

    # Function to validate if username already exists
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            flash('Username already exists.', 'danger')
            raise ValidationError('Username already exists.')
        
    # Function to validate if email already exists
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            flash('Email already exists.', 'danger')
            raise ValidationError('Email already exists.')

# Form for User Login
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField("Login")
class ResetPasswordForm(FlaskForm):
    
    password = PasswordField("Enter Password", validators=[InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField("Confirm Password", 
                                     validators=[InputRequired(), Length(min=8, max=80), 
                                                 EqualTo('password', message="Passwords must match")])
    submit = SubmitField("Reset Password")

    

    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')


    
    