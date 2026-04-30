from flask import Blueprint, jsonify, request
from services.user_task_service import get_all_user_tasks_info_by_student_id
from services.priority_task_service import get_prioritized_tasks_by_student_id
from middlewares.user_middleware import token_required

user_task_bp = Blueprint("user_task", __name__)


@user_task_bp.route("/tasks", methods=["GET"])
@token_required
def get_tasks():
    student_id = request.current_user
    tasks = get_all_user_tasks_info_by_student_id(student_id)
    for t in tasks:
        if t.get("course_name") and len(t["course_name"]) > 3:
            t["course_name"] = t["course_name"][:-3]
    return jsonify({"data": tasks}), 200

@user_task_bp.route("/priority_tasks", methods=["GET"])
@token_required
def get_priority_tasks():
    student_id = request.current_user
    p_tasks = get_prioritized_tasks_by_student_id(student_id)
    for t in p_tasks:
        if t.get("course_name") and len(t["course_name"]) > 3:
            t["course_name"] = t["course_name"][:-3]
    return jsonify({"data": p_tasks}), 200