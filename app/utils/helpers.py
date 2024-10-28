import os
from uuid import uuid4
from datetime import datetime
from bson import ObjectId  
from config import Config

PIZZA_TYPES = ["Cheese", "Salami", "Veggie", "Donair", "Zaatar"]

def serialize_mongo_doc(doc):
    if isinstance(doc, dict):
        return {k: serialize_mongo_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):  # Convert ObjectId to string
        return str(doc)
    elif isinstance(doc, datetime):  # Convert datetime to ISO format
        return doc.isoformat()
    return doc

def get_order_file_path(date, user_id):
    order_dir = os.path.join(Config.ORDERS_DIR, date)
    if not os.path.exists(order_dir):
        os.makedirs(order_dir)
    unique_filename = f"{user_id}_{uuid4()}.json"
    return os.path.join(order_dir, unique_filename)

# helpers.py
from config import Config

PIZZA_TYPES = ["Cheese", "Salami", "Veggie", "Donair", "Zaatar"]

def calculate_totals(data):
    """Calculate the total number of pizza slices and juice boxes."""
    total_slices = {ptype: 0 for ptype in PIZZA_TYPES}
    total_juice_boxes = 0

    # Iterate over all orders and sum up the slices and juice boxes
    for order in data:
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
