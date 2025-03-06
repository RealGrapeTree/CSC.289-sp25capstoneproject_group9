from flask import Blueprint, request, jsonify
from extensions import db
from models import Inventory,InventoryTransaction

from .helper import get_inventory_by_id, get_inventory_by_book_id, update_inventory_stock, log_transaction

# Define Blueprint
inventory_api = Blueprint("inventory_api", __name__, url_prefix="/api/inventory")

# Create Inventory Record
@inventory_api.route("/", methods=["POST"])
def create_inventory():
    data = request.get_json()
    book_id = data.get("book_id")
    quantity = data.get("quantity")
    
    # Retrieve or create inventory entry
    inventory_entry = get_inventory_by_book_id(book_id)
    if not inventory_entry:
        inventory_entry = Inventory(book_id=book_id, stock=quantity)
        db.session.add(inventory_entry)
    else:
        inventory_entry.stock += quantity
    
    db.session.commit()

    # Log the transaction in InventoryTransaction
    log_transaction(book_id, "restock", quantity)

    return jsonify({"message": "Inventory record created or updated"}), 201


# Get All Inventory Records
@inventory_api.route("/", methods=["GET"])
def get_inventory():
    inventory = Inventory.query.all()
    return jsonify([entry.to_dict() for entry in inventory]), 200


@inventory_api.route("/<int:inventory_id>", methods=["GET"])
def get_inventory_record(inventory_id):
    inventory_entry = Inventory.query.get(inventory_id)
    if not inventory_entry:
        return jsonify({"error": "Inventory record not found"}), 404

    return jsonify(inventory_entry.to_dict()), 200


# Update Inventory Record**
@inventory_api.route("/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    inventory_entry = get_inventory_by_id(inventory_id)
    if not inventory_entry:
        return jsonify({"error": "Inventory record not found"}), 404

    data = request.get_json()
    change_type = data.get("change_type")
    quantity = data.get("quantity")

    # Update inventory stock based on change_type
    update_inventory_stock(inventory_entry, change_type, quantity)

    # Log the transaction in InventoryTransaction
    log_transaction(inventory_entry.book_id, change_type, quantity)

    return jsonify({"message": f"Inventory record updated for {change_type}."}), 200


# Delete Inventory Record
@inventory_api.route("/<int:inventory_id>", methods=["DELETE"])
def delete_inventory(inventory_id):
    inventory_entry = get_inventory_by_id(inventory_id)
    if not inventory_entry:
        return jsonify({"error": "Inventory record not found"}), 404

    db.session.delete(inventory_entry)
    db.session.commit()
    return jsonify({"message": "Inventory record deleted"}), 200


# Process Sale (Connect to Sales Transaction)
@inventory_api.route("/sale", methods=["POST"])
def process_sale():
    data = request.get_json()
    book_id = data.get("book_id")
    quantity_sold = data.get("quantity")

    # Check inventory stock before processing the sale
    inventory_entry = get_inventory_by_book_id(book_id)
    if not inventory_entry or inventory_entry.stock < quantity_sold:
        return jsonify({"error": "Not enough stock"}), 400

    # Reduce stock and update transaction history
    inventory_entry.stock -= quantity_sold
    db.session.commit()

    # Log the sale in InventoryTransaction
    log_transaction(book_id, "sale", -quantity_sold)

    return jsonify({"message": "Sale processed successfully"}), 200

@inventory_api.route("/transactions", methods=["GET"])
def get_inventory_transactions():
    transactions = InventoryTransaction.query.all()  # Query all transactions
    return jsonify([transaction.to_dict() for transaction in transactions]), 200