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


# Inventory class represents the stock of books in the system.
# It tracks changes in inventory due to restocking, sales, or damaged books.
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    stock = db.Column(db.Integer, default=0)  # Represents the current stock of books

    book = db.relationship('Book', backref=db.backref('inventory', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "stock": self.stock
        }


# InventoryTransaction class logs all inventory-related transactions.
# It helps maintain a history of stock changes for tracking and auditing.

class InventoryTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    change_type = db.Column(db.String(50), nullable=False)  # 'sale', 'restock', 'damaged'
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    book = db.relationship('Book', backref=db.backref('inventory_transactions', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "change_type": self.change_type,
            "quantity": self.quantity,
            "timestamp": self.timestamp
        }

# Define Transaction model for storing payment records
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)  # Amount in cents
    status = db.Column(db.String(50), nullable=False)  # 'pending', 'completed', 'failed'
    stripe_payment_id = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, amount, status, stripe_payment_id):
        self.amount = amount
        self.status = status
        self.stripe_payment_id = stripe_payment_id

    def __repr__(self):
        return f'<Transaction {self.id} - {self.status}>'
    