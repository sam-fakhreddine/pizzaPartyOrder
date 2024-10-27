from app.app import MongoJSONEncoder
from flask import Blueprint, request, jsonify, make_response, current_app
from bson import ObjectId
import os
import json
from uuid import uuid4
from datetime import datetime

# Initialize Blueprint for order management
orders_bp = Blueprint('orders', __name__)

PIZZA_TYPES = ["Cheese", "Salami", "Veggie", "Donair", "Zaatar"]
ORDERS_DIR = "./orders/"
DISPLAY_LIMIT = 5  # Number of recent orders to display

# Ensure orders directory exists
if not os.path.exists(ORDERS_DIR):
    os.makedirs(ORDERS_DIR)

def serialize_mongo_doc(doc):
    if isinstance(doc, dict):
        return {k: serialize_mongo_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    return doc

def get_order_file_path(date, user_id):
    order_dir = os.path.join(ORDERS_DIR, date)
    if not os.path.exists(order_dir):
        os.makedirs(order_dir)
    unique_filename = f"{user_id}_{uuid4()}.json"
    return os.path.join(order_dir, unique_filename)

def backup_order_to_json(order_data, date, user_id):
    order_file_path = get_order_file_path(date, user_id)
    with open(order_file_path, "w") as file:
        json.dump(order_data, file, cls=MongoJSONEncoder)

def calculate_totals(data):
    total_slices = {ptype: 0 for ptype in PIZZA_TYPES}
    total_juice_boxes = 0
    all_orders = list(current_app.extensions["pymongo"].db.orders.find({"date": data[0]["date"]})) if data else []

    for order in all_orders:
        pizza_slices = order.get("pizza_slices", {})
        for ptype in PIZZA_TYPES:
            total_slices[ptype] += pizza_slices.get(ptype, 0)
        total_juice_boxes += order.get("juice_boxes", 0)

    return total_slices, total_juice_boxes

def calculate_pizzas_needed(pizza_slices, buffer_percentage=0.1):
    pizzas_needed = {}
    for ptype, slices in pizza_slices.items():
        slices_with_buffer = slices * (1 + buffer_percentage)
        pizzas_needed[ptype] = (int(slices_with_buffer) + 9) // 10
    return pizzas_needed

@orders_bp.route("/orders", methods=["POST"])
def submit_order():
    try:
        data = request.json
        date = request.args.get("date")
        user_id = data.get("user_id")

        if not date or not user_id:
            return jsonify({"error": "Missing date or user_id"}), 400
        if not isinstance(data.get("pizza_slices"), dict):
            return jsonify({"error": "Invalid pizza_slices format"}), 400

        order_data = {
            "user_id": user_id,
            "student_name": data.get("student_name", "Unknown"),
            "pizza_slices": data.get("pizza_slices", {}),
            "juice_boxes": data.get("juice_boxes", 0),
            "parent_volunteer": data.get("parent_volunteer", False),
            "date": date,
            "timestamp": datetime.utcnow(),
        }

        result = current_app.extensions["pymongo"].db.orders.insert_one(order_data)
        order_data["_id"] = result.inserted_id
        response_data = serialize_mongo_doc(order_data)
        backup_order_to_json(response_data, date, user_id)

        response = make_response(
            jsonify({"message": "Order submitted successfully", "order": response_data})
        )
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    except Exception as e:
        return jsonify({"error": f"Error saving order: {str(e)}"}), 500

@orders_bp.route("/orders", methods=["GET"])
def get_orders():
    try:
        date = request.args.get("date")
        if not date:
            return jsonify({"error": "Missing date"}), 400

        # Check if PyMongo is initialized
        if "pymongo" not in current_app.extensions:
            raise Exception("MongoDB connection not initialized. Check PyMongo setup.")

        recent_orders = list(
            current_app.extensions["pymongo"].db.orders.find({"date": date})
            .sort("timestamp", -1)
            .limit(DISPLAY_LIMIT)
        )
        serialized_orders = serialize_mongo_doc(recent_orders)
        total_slices, total_juice_boxes = calculate_totals(serialized_orders)
        pizzas_needed = calculate_pizzas_needed(total_slices)

        result = {
            "orders": serialized_orders,
            "total_slices": total_slices,
            "pizzas_needed": pizzas_needed,
            "total_juice_boxes": total_juice_boxes,
        }

        response = make_response(jsonify(result))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    except Exception as e:
        # Enhanced error logging
        error_message = f"Error retrieving orders: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500

