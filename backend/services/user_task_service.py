from model.user_task_model import save_user_task, update_task_status, get_all_user_task_and_assignment_info_by_user_id
from model.user_model import get_user_by_student_id
from model.assignment_model import get_assignment_by_assignment_id
from services.moodle_api_service import fetch_courses
from config import MOODLE_VIEW_URL

from datetime import datetime


def get_all_user_tasks_info_by_student_id(student_id):
    user = get_user_by_student_id(student_id)
    if user is None: return []
    user_id = user.get("data").get("user_id")

    tasks_data =  get_all_user_task_and_assignment_info_by_user_id(user_id)
    
    return tasks_data