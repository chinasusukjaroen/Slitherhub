
from datetime import datetime, timedelta


from services.user_task_service import get_all_user_tasks_info_by_student_id
import re



# ---------------------------------------------------------------------------
# Keyword Patterns  (Thai + English, case-insensitive)
# ---------------------------------------------------------------------------
_HIGH_KEYWORDS = re.compile(
    r"final|exam|สอบ|โปรเจกต์|โปรเจค|project|thesis|วิทยานิพนธ์|"
    r"รายงาน|report|ด่วน|urgent|เก็บคะแนน|midterm|สอบกลางภาค|"
    r"สอบปลายภาค|defense|นำเสนอ|present",
    re.IGNORECASE,
)

_MID_KEYWORDS = re.compile(
    r"assignment|quiz|งาน|แบบฝึกหัด|exercise|lab|laboratory|"
    r"discussion|การบ้าน|ส่งงาน|submit|homework|task",
    re.IGNORECASE,
)

_LOW_KEYWORDS = re.compile(
    r"review|ทบทวน|ประกาศ|announcement|poll|แจ้งข่าว|news|"
    r"survey|แบบสอบถาม|optional|ไม่บังคับ",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Scoring Helpers
# ---------------------------------------------------------------------------
def _urgency_score(hours_left):
    """Component 1 — time urgency (max 60 pts)."""
    if hours_left <= 24:
        return 60
    if hours_left <= 72:      # <= 3 days
        return 45
    if hours_left <= 168:     # <= 7 days
        return 30
    if hours_left <= 336:     # <= 14 days
        return 15
    return 5


def _keyword_score(title, description, course_name):
    """Component 2 — keyword weight (max 30 pts)."""
    text = f"{title} {description} {course_name}"
    if _HIGH_KEYWORDS.search(text):
        return 30
    if _MID_KEYWORDS.search(text):
        return 20
    if _LOW_KEYWORDS.search(text):
        return 10
    return 15   # default when no keyword matched


def _duration_score(deadline, created_at):
    """Component 3 — allowed duration (max 10 pts)."""
    duration_hours = (deadline - created_at).total_seconds() / 3600
    if duration_hours < 24:
        return 10
    if duration_hours < 72:
        return 7
    return 2


def _priority_level(score):
    if score >= 80:
        return "URGENT"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# Main Public Function
# ---------------------------------------------------------------------------
def calculate_priorities(tasks, now=None):

    if now is None: now = datetime.now()

    result = []

    for task in tasks:
        assignment_id = task.get("assignment_id")
        title = task.get("title", "")
        description = task.get("description", "")
        course_name = task.get("course_name", "")

        created_at = datetime.strptime(task["created_at"], "%Y-%m-%d %H:%M:%S")
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d %H:%M:%S")
        

        hours_left = (deadline - now).total_seconds() / 3600

        u_score = _urgency_score(hours_left)
        k_score = _keyword_score(title, description, course_name)
        d_score = _duration_score(deadline, created_at)

        total = u_score + k_score + d_score
        priority_level = _priority_level(total) if hours_left > 0 else "LATE"
        
        result.append({
            "assignment_id": assignment_id,
            "title": title,
            "course_name": course_name,
            "deadline": task["deadline"],
            "hours_left": round(hours_left, 2),
            "urgency_score": u_score,
            "keyword_score": k_score,
            "duration_score": d_score,
            "priority_score": total,
            "priority_level": priority_level ,
        })

    # Sort: priority_score DESC → hours_left ASC (tiebreaker)
    result.sort(key=lambda t: (-t["priority_score"], t["hours_left"]))

    return result


# ---------------------------------------------------------------------------
# Integration Layer
# ---------------------------------------------------------------------------
def get_prioritized_tasks_by_student_id(student_id, now=None):

    tasks = get_all_user_tasks_info_by_student_id(student_id)

    if not tasks: return []

    return calculate_priorities(tasks, now)


# ---------------------------------------------------------------------------
# Demo / Quick Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    FAKE_NOW = datetime.now()

    sample_tasks = [
        {
            "task_id": 1,
            "title": "Final Exam — Computer Networks",
            "description": "Closed-book สอบปลายภาค ห้าม open internet",
            "course_name": "CN401 Computer Networks",
            "deadline": FAKE_NOW + timedelta(hours=30),
            "created_at": FAKE_NOW + timedelta(hours=10),
        },
        {
            "task_id": 2,
            "title": "Lab 5 — TCP/IP",
            "description": "แบบฝึกหัด wireshark packet capture",
            "course_name": "CN401 Computer Networks",
            "deadline": FAKE_NOW + timedelta(hours=300),
            "created_at": FAKE_NOW + timedelta(hours=30),
        },
        {
            "task_id": 3,
            "title": "ประกาศแจ้งข่าว — ปิดระบบชั่วคราว",
            "description": "ระบบ Moodle จะปิดให้บริการ 00:00-02:00 วันพฤหัส",
            "course_name": "ฝ่ายวิชาการ",
            "deadline": FAKE_NOW + timedelta(hours=5),
            "created_at": FAKE_NOW + timedelta(hours=30),
        },
        {
            "task_id": 4,
            "title": "โปรเจกต์กลุ่ม — ระบบ E-Commerce",
            "description": "นำเสนอ demo และส่ง report พร้อม source code",
            "course_name": "SE302 Software Engineering",
            "deadline": FAKE_NOW + timedelta(hours=111),
            "created_at": FAKE_NOW + timedelta(hours=30),
        },
        {
            "task_id": 5,
            "title": "Quiz 3 — Data Structures",
            "description": "MCQ 20 ข้อ ใช้เวลา 30 นาที",
            "course_name": "CS201 Data Structures",
            "deadline": FAKE_NOW + timedelta(hours=10),
            "created_at": FAKE_NOW + timedelta(hours=30),
        },
    ]

    output = calculate_priorities(sample_tasks, now_unix=FAKE_NOW)
    print(json.dumps(output, ensure_ascii=False, indent=2))