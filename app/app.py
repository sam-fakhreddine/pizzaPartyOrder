from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import os
import json
from uuid import uuid4

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS globally

ORDERS_DIR = './orders/'

# Ensure orders directory exists
if not os.path.exists(ORDERS_DIR):
    os.makedirs(ORDERS_DIR)

PIZZA_TYPES = ['Cheese', 'Salami', 'Veggie', 'Donair', 'Zaatar']

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def get_order_file_path(date, user_id):
    """Get the file path for a user's order based on the date and user ID."""
    order_dir = os.path.join(ORDERS_DIR, date)
    if not os.path.exists(order_dir):
        os.makedirs(order_dir)
    unique_filename = f'{user_id}_{uuid4()}.json'  # Use UUID to avoid filename collision
    return os.path.join(order_dir, unique_filename)


def get_orders_for_date(date):
    """Retrieve all orders for a specific date."""
    order_dir = os.path.join(ORDERS_DIR, date)
    if not os.path.exists(order_dir):
        return []

    orders = []
    for order_file in os.listdir(order_dir):
        try:
            with open(os.path.join(order_dir, order_file), 'r') as file:
                orders.append(json.load(file))
        except json.JSONDecodeError:
            continue  # Skip corrupted files gracefully
    return orders


def calculate_totals(data):
    """Calculate the total number of pizza slices and juice boxes."""
    total_slices = {ptype: 0 for ptype in PIZZA_TYPES}
    total_juice_boxes = 0

    for order in data:
        pizza_slices = order.get('pizza_slices', {})
        if not isinstance(pizza_slices, dict):
            continue  # Skip orders with invalid pizza_slices structure

        for ptype in PIZZA_TYPES:
            total_slices[ptype] += pizza_slices.get(ptype, 0)
        total_juice_boxes += order.get('juice_boxes', 0)

    return total_slices, total_juice_boxes


def calculate_pizzas_needed(pizza_slices, buffer_percentage=0.1):
    """Calculate the number of whole pizzas needed based on the slices, with a buffer."""
    pizzas_needed = {}
    for ptype, slices in pizza_slices.items():
        slices_with_buffer = slices * (1 + buffer_percentage)
        pizzas_needed[ptype] = (int(slices_with_buffer) + 9) // 10  # Round up to the nearest whole pizza
    return pizzas_needed


@app.route('/')
def index():
    """Render the index.html template."""
    return render_template('index.html')


@app.route('/orders', methods=['POST'])
def submit_order():
    """API endpoint to submit an order for a specific date."""
    data = request.json
    date = request.args.get('date')
    user_id = data.get('user_id')

    # Validate input data
    if not date or not user_id:
        return jsonify({'error': 'Missing date or user_id'}), 400
    if not isinstance(data.get('pizza_slices'), dict):
        return jsonify({'error': 'Invalid pizza_slices format'}), 400

    order_data = {
        'user_id': user_id,
        'student_name': data.get('student_name', 'Unknown'),
        'pizza_slices': data.get('pizza_slices', {}),
        'juice_boxes': data.get('juice_boxes', 0),
        'parent_volunteer': data.get('parent_volunteer', False),
        'date': date
    }

    try:
        # Write the order to a JSON file
        order_file_path = get_order_file_path(date, user_id)
        with open(order_file_path, 'w') as file:
            json.dump(order_data, file)
    except IOError as e:
        return jsonify({'error': f'File error: {str(e)}'}), 500

    response = make_response(jsonify({'message': 'Order submitted successfully'}))
    response.headers.add("Access-Control-Allow-Origin", "*")  # Adjust in production
    return response, 200


@app.route('/orders', methods=['GET'])
def get_orders():
    """API endpoint to get all orders for a specific date."""
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Missing date'}), 400

    orders = get_orders_for_date(date)
    total_slices, total_juice_boxes = calculate_totals(orders)
    pizzas_needed = calculate_pizzas_needed(total_slices)

    result = {
        'orders': orders,
        'total_slices': total_slices,
        'pizzas_needed': pizzas_needed,
        'total_juice_boxes': total_juice_boxes
    }

    response = make_response(jsonify(result))
    response.headers.add("Access-Control-Allow-Origin", "*")  # Adjust in production
    return response, 200

@app.route('/health')
def health():
    """Health check endpoint to confirm the app is running."""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  # Run on all interfaces in Docker
