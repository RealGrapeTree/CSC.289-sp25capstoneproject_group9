from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# Define Book model using SQLAlchemy
# class Book(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     isbn = db.Column(db.String(20), unique=True, nullable=False)
#     sku = db.Column(db.String(20), unique=True, nullable=True)
#     title = db.Column(db.String(255), nullable=False)
#     stock = db.Column(db.Integer, default=0)
#     price = db.Column(db.Float, nullable=False)

# # Create the database and tables
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         print("Books table created successfully.")
# import os
# print("Current working directory:", os.getcwd())

# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'books.db')
