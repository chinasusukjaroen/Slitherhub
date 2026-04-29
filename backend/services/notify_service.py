# services/notify_service.py
import sqlite3
from database import get_conn  # ✅ ใช้จาก database.py ตรงตามมาตรฐานโปรเจกต์


def get_upcoming_deadlines(hours_ahead=72):
    """
    ดึงงานที่ใกล้ deadline (ค่าเริ่มต้น 3 วัน = 72 ชม.)
    + ยังไม่แจ้งเตือน + ผู้ใช้มีอีเมล + สถานะไม่ใช่ done
    """
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            a.assignment_id,
            a.title,
            a.course_name,
            a.deadline,
            a.source_url,
            u.user_id,
            u.display_name,
            u.email,
            u.student_id,
            ut.user_task_id
        FROM user_tasks ut
        JOIN users u ON ut.user_id = u.user_id
        JOIN assignments a ON ut.assignment_id = a.assignment_id
        WHERE a.is_notified = 0
          AND ut.status != 'done'
          AND u.email IS NOT NULL 
          AND u.email != ''
          AND a.deadline >= datetime('now', 'localtime')
          AND a.deadline <= datetime('now', '+{hours_ahead} hours', 'localtime')
        ORDER BY a.deadline ASC
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_as_notified(user_task_id):
    """
    อัปเดตว่าแจ้งเตือนงานนี้ให้ผู้ใช้คนนี้แล้ว (รายบุคคล)
    ถ้าต้องการมาร์คที่ตาราง assignments ให้เปลี่ยนเป็น assignment_id ได้ตามโครงสร้าง
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_tasks
        SET is_notified = 1, notified_at = datetime('now', 'localtime')
        WHERE user_task_id = ?
    """, (user_task_id,))
    conn.commit()
    conn.close()


def reset_notifications():
    """รีเซ็ตสถานะการแจ้งเตือนทั้งหมด (ใช้ตอน test/debug)"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_tasks
        SET is_notified = 0, notified_at = NULL
    """)
    conn.commit()
    conn.close()


def get_notification_summary():
    """ดูสรุปงานที่แจ้งเตือนแล้ว / ยังไม่แจ้ง"""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) AS total_assignments,
            SUM(CASE WHEN is_notified = 1 THEN 1 ELSE 0 END) AS notified_count,
            SUM(CASE WHEN is_notified = 0 THEN 1 ELSE 0 END) AS pending_count
        FROM user_tasks
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}