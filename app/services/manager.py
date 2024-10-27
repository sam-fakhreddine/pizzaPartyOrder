from flask import Blueprint, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
import os

# Set up MongoDB connection
client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017/"))
db = client['evansdale_pizza']
orders_collection = db['orders']
menu_collection = db['menu']

# Define Blueprint
manager_bp = Blueprint('manager', __name__)

# Redirect unauthenticated users to the login page
@manager_bp.before_request
def require_login():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

# Route to get all orders
@manager_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        orders = list(orders_collection.find({}))
        for order in orders:
            order['_id'] = str(order['_id'])  # Convert ObjectId to string for JSON serialization
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to add new menu item (e.g., pizza flavor or snack)
@manager_bp.route('/menu', methods=['POST'])
def add_menu_item():
    item_data = request.json
    if "name" in item_data and "type" in item_data:  # Ensure name and type are provided
        try:
            menu_collection.insert_one(item_data)
            return jsonify({"message": "Menu item added successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Name and type are required"}), 400
