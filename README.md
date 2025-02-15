# Novel Solution 
A Novel Solution aims to provide an efficient system for managing bookstore 
inventory and point-of-sale (POS) operations. 

## Book Search Feature
The Book-Search branch implements the **book search functionality** for the *A Novel Solution* project.  
Users can search for books by **ISBN or SKU**, retrieving details like title, price, and stock availability. 

### **Features**  
- Fetches book details from an API (Open Library).  
- Stores book data in an SQLite database.  
- Allows searching for books using ISBN/SKU.  
- Displays search results in a Flask-based web interface.  

### **Setup and Execution**

#### **Set Up the Database** 
Initialize the SQLite database by running:  
setup_db.py 

#### **Fetch Books from API**
- Retrieve book details from an external API and save them to the database: Run fetch_books_from_api.py.
- This script fetches book information and populates the database.

#### **Check Stored Books**
- Verify if books have been successfully added to the database: Run check_books.py.
- This script ensures that the data is stored correctly.

#### **Run the Book Search Feature**
- Start the Flask app to enable book searching.
- Run book-search.py to search for books by ISBN in the database. The script will display book details (title, stock, price) if found.

### Project Structure:

```
book-search/
│── database/
│   ├── setup_db.py            # Initializes SQLite database  
│   ├── check_books.py         # Verifies stored book data  
│── scripts/
│   ├── fetch_books_from_api.py # Fetches book details from API  
│── app/
│   ├── book-search.py         # Flask-based book search  
│── .gitignore  
│── README.md  
│── requirements.txt  
```



