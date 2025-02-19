from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


from extensions import db, bcrypt, login_manager


# Create a User model that works with Flask-Login
class User(db.Model, UserMixin):  # Inherit from UserMixin to get default implementation of required methods
    username = db.Column(db.String(20), primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'cashier' or 'manager'

    def get_id(self):
        return str(self.username)

    def __repr__(self):
        return f'<User {self.username} - {self.role}>'
    


# Define Book model using SQLAlchemy
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    sku = db.Column(db.String(20), unique=True, nullable=True)
    title = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    number_of_pages = db.Column(db.Integer, nullable=True)
    authors = db.Column(db.String(255), nullable=True)
    publishers = db.Column(db.String(255), nullable=True)
    publish_date = db.Column(db.String(20), nullable=True)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    cover = db.Column(db.String(255), nullable=True)
    

    

