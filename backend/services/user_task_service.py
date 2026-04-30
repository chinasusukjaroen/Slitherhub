from model.user_task_model import UserTaskModel
from model.user_model import UserModel
from services.moodle_api_service import fetch_courses
from config import MOODLE_VIEW_URL

from datetime import datetime

userTaskModel = UserTaskModel.get_instance()
userModel = UserModel.get_instance()

def get_all_user_tasks_info_by_student_id(student_id):
    user = userModel.get_user_by_student_id(student_id)
    if user is None:
        return []

    user_data = user.get("data") or user
    user_id = user_data.get("user_id")

    if user_id is None:
        return []

    tasks_data = userTaskModel.get_all_user_task_and_assignment_info_by_user_id(user_id)
    return tasks_data