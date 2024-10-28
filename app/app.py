from flask import Flask
from flask_cors import CORS
from encoder import MongoJSONEncoder
from db import init_db
from config import Config
import routes

app = Flask(__name__)
app.config.from_object(Config)  
CORS(app, supports_credentials=True)

app.json_encoder = MongoJSONEncoder
init_db(app)

app.register_blueprint(routes.bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
