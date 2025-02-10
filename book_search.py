from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    sku = db.Column(db.String(20), unique=True, nullable=True)
    title = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Route to search for a book by ISBN or SKU
@app.route('/search', methods=['GET'])
def search_book():
    search_term = request.args.get('q', '')  # Get search term from URL query parameter
    book = Book.query.filter((Book.isbn == search_term) | (Book.sku == search_term)).first()

    if book:
        return jsonify({
            "title": book.title,
            "stock": book.stock,
            "price": f"${book.price:.2f}"
        })
    else:
        return jsonify({"error": "Book not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
