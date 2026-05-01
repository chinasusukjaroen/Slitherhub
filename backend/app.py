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
from apscheduler.schedulers.background import BackgroundScheduler
from services.notify_service import get_upcoming_deadlines, mark_as_notified
 
# ตั้งค่า Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
 
app = Flask(__name__)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)
 
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(assignment_bp, url_prefix="/api")
app.register_blueprint(user_task_bp, url_prefix="/api")
 
 
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "web"}), 200
 
 
def run_notify():
    from services.email_service import send_email
    deadlines = get_upcoming_deadlines(hours_ahead=72)
    for task in deadlines:
        task['name'] = task['display_name']
        success = send_email(task['email'], task)
        if success:
            mark_as_notified(task['user_task_id'])
 
 
if __name__ == "__main__":
    logging.info("Starting Flask server on port 5000...")
    init_db()
 
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_notify, 'cron', hour=0, minute=0)  # รันทุกเที่ยงคืน
    scheduler.start()
    logging.info(" Scheduler เริ่มทำงานแล้ว (ทุกวันเที่ยงคืน)")
    run_notify()  
 
    app.run(debug=True, port=5000, host="0.0.0.0", use_reloader=False)