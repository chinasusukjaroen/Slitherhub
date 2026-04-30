from flask import Blueprint, jsonify, request
# from model.assignment_model import get_all_assignments
from model.user_task_model import UserTaskModel
from services.moodle_api_service import sync_assignments
from middlewares.user_middleware import token_required

assignment_bp = Blueprint("assignment", __name__)

userTaskModel = UserTaskModel.get_instance()

@assignment_bp.route("/sync_assignments", methods=["POST"])
@token_required
def controller_sync_assignments():
    student_id = request.current_user
    info = sync_assignments(student_id)
    return jsonify(info), 200

@assignment_bp.route("/notifications/pending", methods=["GET"])
@token_required
def get_pending():
    tasks = userTaskModel.get_pending_notifications()
    return jsonify({"tasks": tasks}), 200