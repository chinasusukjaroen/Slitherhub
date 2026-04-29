# app.py
import logging
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from controllers.user_controller import auth_bp
from controllers.user_task_controller import user_task_bp
from controllers.assignment_controller import assignment_bp
from database import init_db
from config import ALLOWED_ORIGINS

# ✅ Import config
from config import ALLOWED_ORIGINS

# ตั้งค่า Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",

)

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)


app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(assignment_bp, url_prefix="/api")
app.register_blueprint(user_task_bp, url_prefix="/api")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "web"}), 200

if __name__ == "__main__":
    logging.info("🚀 Starting Flask server on port 5000...")
    init_db()   
    app.run(debug=True, port=5000, host="127.0.0.1", use_reloader=False)