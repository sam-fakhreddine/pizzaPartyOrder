from flask import Blueprint, jsonify, request, make_response, render_template, send_from_directory

from services.order_service import save_order, backup_order_to_json
from utils.helpers import serialize_mongo_doc, calculate_totals, calculate_pizzas_needed
from db import mongo
from config import Config
from datetime import datetime
import os
bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(bp.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )

@bp.route("/orders", methods=["POST"])
def submit_order():
    """Handles order submissions."""
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

        response_data = save_order(order_data)
        backup_order_to_json(response_data, date, user_id)

        response = make_response(
            jsonify({"message": "Order submitted successfully", "order": response_data})
        )
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    except Exception as e:
        return jsonify({"error": f"Error saving order: {str(e)}"}), 500

@bp.route("/orders", methods=["GET"])
def get_orders():
    """Retrieve orders for a specific date."""
    try:
        date = request.args.get("date")
        if not date:
            return jsonify({"error": "Missing date"}), 400

        # Fetch and serialize recent orders for the specified date
        recent_orders = list(
            mongo.db.orders.find({"date": date})
            .sort("timestamp", -1)
            .limit(Config.DISPLAY_LIMIT)
        )
        serialized_orders = serialize_mongo_doc(recent_orders)

        # Calculate totals for all orders on the specified date
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



@bp.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200
