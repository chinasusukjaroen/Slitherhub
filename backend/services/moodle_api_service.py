from datetime import datetime, timezone, timedelta
from backend.model.user_model import update_moodle_user_id, get_moodle_user_id_by_student_id, update_moodle_api, get_user_by_student_id
from backend.model.assignment_model import get_assignment_by_moodle_id, save_assignment, update_assignment_deadline_and_description, get_assignment_by_assignment_id
from backend.model.user_task_model import get_user_task_by_user_id_and_assignment_id, save_user_task, update_task_status, get_user_tasks_by_user_id
from backend.model.TaskStatus import TaskStatus
import requests

MOODLE_API_URL_LOGIN = "https://courses.cs.tu.ac.th/login/token.php"
MOODLE_API_URL_GET = "https://courses.cs.tu.ac.th/webservice/rest/server.php"
MOODLE_VIEW_URL = "https://courses.cs.tu.ac.th/mod/assign/view.php?id="

def safe_call_database_func(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        if result.get("success") is True:
            return result.get("data")

        return None
    except Exception as e:
        print(f"[safe_call_database] error: {e}")
        return None

def convert_moodle_time_to_datetime(ts):
    dt_str = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(
        timezone(timedelta(hours=7))
    ).strftime("%Y-%m-%d %H:%M:%S")

    return dt_str

def login_moodle(username, password):
    try:
        payload = {
            "username": username,
            "password": password,
            "service": "moodle_mobile_app"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        res = requests.post(MOODLE_API_URL_LOGIN, data=payload, headers=headers, timeout=20)
        data = res.json()


        if data.get("token"):
            token = data.get("token")
            update_moodle_api(username, token)
            
            moodle_user_id = safe_call_database_func(get_moodle_user_id_by_student_id, username)

            if moodle_user_id == None:
                fetch_user_info = fetch_user_info_and_save(token, username)
                if fetch_user_info.get("success") == False:
                    return fetch_user_info
            
            # fetch_assignments_info = fetch_assignments_and_save(token, username)
            # if fetch_assignments_info.get("status") == False:
            #         print(fetch_assignments_info)
            #         return fetch_assignments_info

            return {
                "status": True,
                "token": token,
            }
        
        return {"success": False, "message": data.get("message", "Login ไม่สำเร็จ")}
    except Exception as e:
        print("เกิดข้อผิดพลาดตอน Login", e)
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}

def fetch_user_info_and_save(token, username):
    try:
        payload = {
            "wstoken": token,
            "wsfunction": "core_webservice_get_site_info",
            "moodlewsrestformat": "json"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        res = requests.post(MOODLE_API_URL_GET, data=payload, headers=headers, timeout=10)
        data = res.json()
        if data.get("userid"):
            status = update_moodle_user_id(username, data.get("userid")).get("success")

            tMessage = "บันทึกสำเร็จ"
            if status == False: tMessage = "บันทึกไม่สำเร็จ"
            
            return {"success": status, "message" : tMessage}
        
        return {"success": False, "message": data.get("message", "ใช้งาน Token ไม่สำเร็จ")}

    except Exception as e:
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}



def sync_assignments(student_id):
    user = safe_call_database_func(get_user_by_student_id, student_id)

    if not user: return {"success": False, "message" : "ไม่พบ user"}

    token = user.get("moodle_API")
    if  not token: return {"success": False, "message" : "ไม่พบ moodle token"}

    fetch_assignments_info = fetch_assignments_and_save(token, student_id)

    if fetch_assignments_info.get("success") == False:
        print(fetch_assignments_info)
        return {"success": False, "message": fetch_assignments_info.get("message", "ใช้งาน Token ไม่สำเร็จ")}
    
    return {"success": True, "message" : "Sync assignments สำเร็จ"}




def fetch_assignments_and_save(token, student_id):
    try:
        
        payload = {
            "wstoken": token,
            "wsfunction": "mod_assign_get_assignments",
            "moodlewsrestformat": "json",
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        res = requests.post(MOODLE_API_URL_GET, data=payload, headers=headers, timeout=10)
        data = res.json()

        assignments = []

        if not data.get("courses"): return {"success": False, "message": data.get("message", "ใช้งาน Token ไม่สำเร็จ")}

        user = safe_call_database_func(get_user_by_student_id, student_id)
        if not user: return {"success": False, "message": "ไม่พบ user "}
        
        user_id = user.get("user_id")

        for course in data.get("courses"):
            course_id = course.get("id")
            course_name = course.get("shortname")

            for assignment in course.get("assignments"):
                moodle_assignment_uid = assignment.get("id")
                description = assignment.get("intro")
                deadline = convert_moodle_time_to_datetime(assignment.get("duedate"))
                
                title = assignment.get("name")
                dataReturn = {}
                dataReturn["title"] = title
                dataReturn["course_id"] = course_id
                dataReturn["deadline"] = deadline
                dataReturn["description"] = description


                assignment_id = None
                if not safe_call_database_func(get_assignment_by_moodle_id, moodle_assignment_uid):
                    source_url = MOODLE_VIEW_URL + str(assignment.get("cmid"))
                    assignment_id = safe_call_database_func(save_assignment, moodle_assignment_uid, title, deadline, course_id, course_name, description, source_url)
                    # assignment_id = save_assignment(moodle_assignment_uid, title, deadline, course_id, course_name, description, source_url)
                    
                else:
                    assignment_id = safe_call_database_func(update_assignment_deadline_and_description, moodle_assignment_uid, deadline, description)
                    # assignment_id = update_assignment_deadline_and_description(moodle_assignment_uid, deadline, description)

                assignments.append(dataReturn)

                #Sync user task
                user_task = safe_call_database_func(get_user_task_by_user_id_and_assignment_id, user_id, assignment_id)
                if user_task is None:
                    print("[DEBUG] กำลัง fetch:", moodle_assignment_uid)
                    status = fetch_get_assignment_status(token, moodle_assignment_uid)

                    save_user_task(user_id, assignment_id, status.value)
                    
                else:
                    if user_task.get("status") == TaskStatus.SUBMITTED.value: continue
                    print("[DEBUG] กำลัง fetch:", moodle_assignment_uid)

                    status = fetch_get_assignment_status(token, moodle_assignment_uid)
                    update_task_status(user_id, assignment_id, status.value)

        return {"success": True, "data": assignments}
        
        
    except Exception as e:
        print("เกิดข้อผิดพลาด (fetch assignment and save)", e)
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}

def sync_all_user_tasks(student_id):
    user = safe_call_database_func(get_user_by_student_id, student_id)
    if not user: return False
        

    user_id = user["user_id"]
    token = user["moodle_API"]

    tasks = safe_call_database_func(get_user_tasks_by_user_id, user_id)

    for t in tasks:
        if t["status"] == TaskStatus.SUBMITTED.value:
            continue
        assignment = safe_call_database_func(get_assignment_by_assignment_id, t["assignment_id"])
        if not assignment:
            print("MISSING assignment:", t["assignment_id"])

            continue

        status = fetch_get_assignment_status(
            token,
            assignment["moodle_event_uid"]
        )

        update_task_status(user_id, t["assignment_id"], status.value)

    return True




def fetch_get_assignment_status(token, moodle_assignment_id):
    try:
        payload = {
            "wstoken": token,
            "wsfunction": "mod_assign_get_submission_status",
            "moodlewsrestformat": "json",
            "assignid": moodle_assignment_id
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        res = requests.post(MOODLE_API_URL_GET, data=payload, headers=headers, timeout=10)
        data = res.json()

        lastattempt = data.get("lastattempt") or None 

        if not lastattempt: return TaskStatus.PENDING

        sub = lastattempt.get("submission")

        if not sub: return TaskStatus.PENDING

        status = sub.get("status")
        if status == "submitted": return TaskStatus.SUBMITTED
            

        assignment = safe_call_database_func(get_assignment_by_moodle_id, moodle_assignment_id)

        if assignment is None:
            raise ValueError("Assignment not found")
        
        now = datetime.now()
        dt = datetime.strptime(assignment["deadline"], "%Y-%m-%d %H:%M:%S")
        if now > dt: return TaskStatus.OVERDUE

        return TaskStatus.PENDING

    except Exception as e:
        print("เกิดข้อผิดพลาด (fetch assignment status)", e)
        return TaskStatus.PENDING


def sync_user_task(token, user_id, assignment_id, moodle_assignment_id):
    user_task = safe_call_database_func(get_user_task_by_user_id_and_assignment_id, user_id, assignment_id)

    if user_task is None:
        save_user_task(user_id, assignment_id)
        
    else:
        if user_task.get("status") == TaskStatus.SUBMITTED.value: return True

        status = fetch_get_assignment_status(token, moodle_assignment_id)
        update_task_status(user_id, assignment_id, status.value)
    
    return True

def fetch_courses(token, username):
    try:
        moodle_user_id = safe_call_database_func(get_moodle_user_id_by_student_id, username)
        if moodle_user_id == None: return {"success": False, "message": "ดึง user_id ไม่สำเร็จ"}

        payload = {
            "wstoken": token,
            "wsfunction": "core_enrol_get_users_courses",
            "moodlewsrestformat": "json",
            "userid": moodle_user_id
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        res = requests.post(MOODLE_API_URL_GET, data=payload, headers=headers, timeout=10)
        data = res.json()

        courses = []

        if data:
            for course in data:
                if course.get("id"):
                    courses.append({
                        "id": course.get("id"),
                        "name": course.get("shortname")
                        })

            return {"success": True, "data": courses}
        
        return {"success": False, "message": data.get("message", "ใช้งาน Token ไม่สำเร็จ")}

    except Exception as e:
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}