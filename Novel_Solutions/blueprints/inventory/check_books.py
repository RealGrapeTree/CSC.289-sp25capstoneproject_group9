# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

# # Initialize Flask app and SQLAlchemy
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # Define Book model using SQLAlchemy
# class Book(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     isbn = db.Column(db.String(20), unique=True, nullable=False)
#     sku = db.Column(db.String(20), unique=True, nullable=True)
#     title = db.Column(db.String(255), nullable=False)
#     stock = db.Column(db.Integer, default=0)
#     price = db.Column(db.Float, nullable=False)

# # Query all books and print them
# # def check_books():
# #     books = Book.query.all()
# #     for book in books:
# #         print(f"ID: {book.id}, ISBN: {book.isbn}, SKU: {book.sku}, Title: {book.title}, Stock: {book.stock}, Price: ${book.price:.2f}")

# # Run the function to check books
# if __name__ == '__main__':
#     with app.app_context():
#         check_books()
