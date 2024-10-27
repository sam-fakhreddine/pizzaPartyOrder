from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
import os
from bson import ObjectId
from json import JSONEncoder
from datetime import datetime

# Import Blueprints
from services.auth import auth_bp
from services.manager import manager_bp
from services.orders import orders_bp

# Instantiate PyMongo without initialization
mongo = PyMongo()

# Custom JSON Encoder for MongoDB ObjectIds
class MongoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.json_encoder = MongoJSONEncoder
    app.config["MONGO_URI"] = "mongodb://mongodb:27017/evansdale_pizza"
    
    # Initialize Mongo with app
    mongo.init_app(app)
    print("PyMongo initialized:", mongo)

    CORS(app, supports_credentials=True)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(orders_bp)

    # Root route for the main application
    @app.route("/")
    def index():
        return render_template("index.html")

    # Test MongoDB connection
    @app.route("/test-mongo")
    def test_mongo():
        try:
            # Attempt to access MongoDB to verify connection
            collections = mongo.db.list_collection_names()
            return jsonify({"collections": collections}), 200
        except Exception as e:
            # Log detailed error message
            error_message = f"MongoDB connection error: {str(e)}"
            print(error_message)
            return jsonify({"error": error_message}), 500

    return app

# Run the app only if it's the main module
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
