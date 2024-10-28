import os
import json
from uuid import uuid4
from config import Config
from db import mongo
from utils.helpers import serialize_mongo_doc, get_order_file_path


def save_order(order_data):
    # Insert the dictionary directly
    result = mongo.db.orders.insert_one(order_data)
    order_data[
        "_id"
    ] = result.inserted_id  # MongoDB automatically generates an ObjectId
    return serialize_mongo_doc(order_data)


def backup_order_to_json(order_data, date, user_id):
    """Save a JSON backup of the order in the configured directory."""
    order_file_path = get_order_file_path(date, user_id)
    # Ensure the orders directory exists
    os.makedirs(Config.ORDERS_DIR, exist_ok=True)
    with open(order_file_path, "w") as file:
        json.dump(order_data, file, default=str)
