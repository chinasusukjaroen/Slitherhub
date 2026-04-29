# services/notify_service.py
import sqlite3
import logging
from database import get_conn  # ✅ ใช้จาก database.py ตรงตามมาตรฐานโปรเจกต์

# ตั้งค่า Logging สำหรับดูสถานะการทำงาน
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_upcoming_deadlines(hours_ahead=72):
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
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_tasks
        SET is_notified = 1
        WHERE user_task_id = ?
    """, (user_task_id,))
    conn.commit()
    conn.close()


def reset_notifications():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_tasks
        SET is_notified = 0, notified_at = NULL
    """)
    conn.commit()
    conn.close()


def get_notification_summary():
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


# ==========================================
# ✅ MAIN BLOCK: รันทดสอบ / ใช้กับ Scheduler
# ==========================================
if __name__ == "__main__":
    try:
        logging.info("🚀 เริ่มต้นระบบตรวจสอบ Deadline...")

        # 1. ดึงงานที่ใกล้ครบกำหนด (ค่าเริ่มต้น 72 ชม. = 3 วัน)
        deadlines = get_upcoming_deadlines(hours_ahead=24)

        if not deadlines:
            logging.info("✅ ไม่พบงานที่ต้องแจ้งเตือนในรอบนี้")
        else:
            logging.info(f"📦 พบงานที่ต้องแจ้งเตือน: {len(deadlines)} รายการ")

            # 2. วนลูปแจ้งเตือน
            for task in deadlines:
                logging.info(f"🔔 แจ้งเตือน -> {task['display_name']} ({task['email']}) | งาน: {task['title']} | Deadline: {task['deadline']}")
                
                # 📧 TODO: ใส่โค้ดส่งอีเมลจริงตรงนี้ เช่น:
                # send_email_notification(task['email'], task['title'], task['deadline'])
                
                # 3. มาร์คว่าแจ้งเตือนแล้ว (ป้องกันการส่งซ้ำ)
                mark_as_notified(task['user_task_id'])
                logging.info(f"✅ อัปเดตสถานะแจ้งเตือนเรียบร้อย (user_task_id: {task['user_task_id']})")

        # 4. แสดงสรุปสถานะหลังรัน
        summary = get_notification_summary()
        logging.info(f"📊 สรุปสถานะ DB: รวม {summary['total_assignments']} | แจ้งแล้ว {summary['notified_count']} | รอแจ้ง {summary['pending_count']}")

    except Exception as e:
        logging.error(f"❌ เกิดข้อผิดพลาดในการรัน notify_service: {e}")
    finally:
        logging.info("🏁 จบการทำงาน notify_service")