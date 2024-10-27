from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
)
from flask_cors import CORS
from flask_pymongo import PyMongo
import os
import json
from uuid import uuid4
from datetime import datetime
from bson import ObjectId
from json import JSONEncoder


class MongoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


app = Flask(__name__)
CORS(app, supports_credentials=True)

# Use custom JSON encoder
app.json_encoder = MongoJSONEncoder

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://mongodb:27017/evansdale_pizza"
mongo = PyMongo(app)

ORDERS_DIR = "./orders/"
DISPLAY_LIMIT = 5  # Number of recent orders to display

# Ensure orders directory exists
if not os.path.exists(ORDERS_DIR):
    os.makedirs(ORDERS_DIR)

PIZZA_TYPES = ["Cheese", "Salami", "Veggie", "Donair", "Zaatar"]


def serialize_mongo_doc(doc):
    """Helper function to serialize MongoDB documents"""
    if isinstance(doc, dict):
        return {k: serialize_mongo_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    return doc


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


def get_order_file_path(date, user_id):
    """Get the file path for a user's order based on the date and user ID."""
    order_dir = os.path.join(ORDERS_DIR, date)
    if not os.path.exists(order_dir):
        os.makedirs(order_dir)
    unique_filename = f"{user_id}_{uuid4()}.json"
    return os.path.join(order_dir, unique_filename)


def backup_order_to_json(order_data, date, user_id):
    """Save a JSON backup of the order."""
    order_file_path = get_order_file_path(date, user_id)
    with open(order_file_path, "w") as file:
        json.dump(order_data, file, cls=MongoJSONEncoder)


def calculate_totals(data):
    """Calculate the total number of pizza slices and juice boxes."""
    total_slices = {ptype: 0 for ptype in PIZZA_TYPES}
    total_juice_boxes = 0

    # Get all orders for totals calculation
    all_orders = list(mongo.db.orders.find({"date": data[0]["date"]})) if data else []

    for order in all_orders:
        pizza_slices = order.get("pizza_slices", {})
        for ptype in PIZZA_TYPES:
            total_slices[ptype] += pizza_slices.get(ptype, 0)
        total_juice_boxes += order.get("juice_boxes", 0)

    return total_slices, total_juice_boxes


def calculate_pizzas_needed(pizza_slices, buffer_percentage=0.1):
    """Calculate the number of whole pizzas needed based on the slices, with a buffer."""
    pizzas_needed = {}
    for ptype, slices in pizza_slices.items():
        slices_with_buffer = slices * (1 + buffer_percentage)
        pizzas_needed[ptype] = (int(slices_with_buffer) + 9) // 10
    return pizzas_needed


@app.route("/")
def index():
    """Render the index.html template."""
    return render_template("index.html")


@app.route("/orders", methods=["POST"])
def submit_order():
    """API endpoint to submit an order for a specific date."""
    try:
        data = request.json
        date = request.args.get("date")
        user_id = data.get("user_id")

        # Validate input data
        if not date or not user_id:
            return jsonify({"error": "Missing date or user_id"}), 400
        if not isinstance(data.get("pizza_slices"), dict):
            return jsonify({"error": "Invalid pizza_slices format"}), 400

        # Order data with timestamp
        order_data = {
            "user_id": user_id,
            "student_name": data.get("student_name", "Unknown"),
            "pizza_slices": data.get("pizza_slices", {}),
            "juice_boxes": data.get("juice_boxes", 0),
            "parent_volunteer": data.get("parent_volunteer", False),
            "date": date,
            "timestamp": datetime.utcnow(),
        }

        # Save to MongoDB
        result = mongo.db.orders.insert_one(order_data)

        # Add MongoDB ObjectId to order data
        order_data["_id"] = result.inserted_id

        # Serialize for response
        response_data = serialize_mongo_doc(order_data)

        # Backup to JSON file
        backup_order_to_json(response_data, date, user_id)

        response = make_response(
            jsonify({"message": "Order submitted successfully", "order": response_data})
        )
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    except Exception as e:
        app.logger.error(f"Error saving order: {str(e)}")
        return jsonify({"error": f"Error saving order: {str(e)}"}), 500


@app.route("/orders", methods=["GET"])
def get_orders():
    """API endpoint to get all orders for a specific date."""
    try:
        date = request.args.get("date")
        if not date:
            return jsonify({"error": "Missing date"}), 400

        # Fetch the 5 most recent orders for display
        recent_orders = list(
            mongo.db.orders.find({"date": date})
            .sort("timestamp", -1)
            .limit(DISPLAY_LIMIT)
        )
        serialized_orders = serialize_mongo_doc(recent_orders)

        # Calculate totals using ALL orders for the date, not just the displayed ones
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
        app.logger.error(f"Error retrieving orders: {str(e)}")
        return jsonify({"error": f"Error retrieving orders: {str(e)}"}), 500


@app.route("/health")
def health():
    """Health check endpoint to confirm the app is running."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
