from extensions import db
from models import Inventory, InventoryTransaction

# Helper function to retrieve inventory entry by inventory_id
def get_inventory_by_id(inventory_id):
    return Inventory.query.get(inventory_id)

# Helper function to retrieve inventory entry by book_id
def get_inventory_by_book_id(book_id):
    return Inventory.query.filter_by(book_id=book_id).first()

# Helper function to update inventory stock
def update_inventory_stock(inventory_entry, change_type, quantity):
    if change_type == "restock":
        inventory_entry.stock += quantity
    elif change_type == "damaged":
        inventory_entry.stock -= quantity
    elif change_type == "sale":
        inventory_entry.stock -= quantity
    elif change_type == "return":
        inventory_entry.stock += quantity
    db.session.commit()

# Helper function to log a transaction in InventoryTransaction
def log_transaction(book_id, change_type, quantity):
    transaction = InventoryTransaction(
        book_id=book_id,
        change_type=change_type,
        quantity=quantity
    )
    db.session.add(transaction)
    db.session.commit()
