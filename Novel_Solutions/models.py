from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from extensions import db, bcrypt, login_manager
from datetime import datetime

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

# Define Transaction model for storing payment records


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)  # Cashier/Manager
    amount = db.Column(db.Integer, nullable=False)  # Amount in cents
    status = db.Column(db.String(50), nullable=False)  # 'pending', 'completed', 'failed', 'refunded'
    stripe_payment_id = db.Column(db.String(100), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)  # Use utcnow + index for better filtering
    
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    items = db.relationship('TransactionItem', backref='transaction', lazy=True)

    def __repr__(self):
        return f'<Transaction {self.id} - {self.status}>'

class TransactionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)  # Store in cents for consistency
    isbn = db.Column(db.String(13), nullable=False)
    book_title = db.Column(db.String(255), nullable=False)

    book = db.relationship('Book', backref=db.backref('transaction_items', lazy=True))

    def __repr__(self):
        return f'<TransactionItem {self.id} - {self.book.title}>'

    