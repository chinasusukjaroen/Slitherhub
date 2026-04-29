# services/notify_service.py
import sqlite3
from database import get_conn
from datetime import datetime


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
    """อัปเดตว่าแจ้งเตือนงานนี้ให้ผู้ใช้คนนี้แล้ว"""
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


# ─── 🆕 ฟังก์ชันใหม่: รันพร้อมพิมพ์สถานะขึ้น Terminal ─────────────
def run_notification_check(send_email_func, hours_ahead=72):
    """
    รันระบบแจ้งเตือนพร้อมแสดง Log บน Terminal
    send_email_func: ฟังก์ชันที่รับ dict task และคืนค่า True/False
                     เช่น: lambda t: send_email(t['email'], t)
    """
    print("\n" + "="*60)
    print("🔔 เริ่มตรวจสอบงานใกล้ครบกำหนด")
    print(f"📅 เวลาปัจจุบัน: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ แจ้งเตือนล่วงหน้า: {hours_ahead} ชั่วโมง")
    print("="*60)

    # 1️⃣ ดึงงาน
    tasks = get_upcoming_deadlines(hours_ahead)
    
    if not tasks:
        print("✅ ไม่พบงานที่ต้องแจ้งเตือนในขณะนี้")
        print("💡 ระบบจะตรวจสอบอีกครั้งในรอบถัดไป")
        return {"found": 0, "sent": 0, "failed": 0}

    print(f"📋 พบงานที่ต้องแจ้งเตือน {len(tasks)} รายการ\n")

    sent = 0
    failed = 0

    # 2️⃣ วนลูปส่ง + อัปเดตสถานะ + พิมพ์ Log
    for i, task in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] 📤 กำลังแจ้งเตือน: {task['display_name']} ({task['student_id']})")
        print(f"      📧 ถึง: {task['email']}")
        print(f"      📝 งาน: {task['title']}")
        print(f"      📚 วิชา: {task['course_name']}")
        print(f"      ⏰ Deadline: {task['deadline']}")

        try:
            # เรียกฟังก์ชันส่งอีเมลที่ผู้ใช้ส่งเข้ามา
            success = send_email_func(task)
            
            if success:
                mark_as_notified(task['user_task_id'])
                print(f"      ✅ ส่งสำเร็จ + อัปเดตสถานะ is_notified = 1")
                sent += 1
            else:
                print(f"      ❌ ส่งอีเมลไม่สำเร็จ (จะลองใหม่ในรอบถัดไป)")
                failed += 1
        except Exception as e:
            print(f"      ❌ เกิดข้อผิดพลาด: {e}")
            failed += 1
        
        print()  # เว้นบรรทัดอ่านง่าย

    # 3️⃣ สรุปผล
    total = sent + failed
    rate = (sent / total * 100) if total > 0 else 0
    print("="*60)
    print("📊 สรุปผลการแจ้งเตือน")
    print("="*60)
    print(f"✅ ส่งสำเร็จ: {sent} รายการ")
    print(f"❌ ส่งล้มเหลว: {failed} รายการ")
    print(f"📈 อัตราสำเร็จ: {rate:.1f}%")
    print("="*60)
    
    return {"found": len(tasks), "sent": sent, "failed": failed}

# ─── 🆕 ส่วนสั่งรันเมื่อเรียกไฟล์ตรงๆ ─────────────────────
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🚀 กำลังเริ่มระบบแจ้งเตือน...")
    
    # พยายาม import ฟังก์ชันส่งอีเมล
    try:
        from services.email_service import send_email
    except ImportError:
        try:
            from services.email_service import send_email
        except ImportError:
            # ถ้ายังไม่มีไฟล์อีเมล ให้ใช้โหมดจำลองก่อน (เพื่อเทสต์หน้าจอ)
            print("⚠️ ไม่พบ email_service → ใช้โหมดจำลอง (ไม่ส่งจริง)")
            def send_email(to_email, task):
                print(f"📧 [MOCK] ส่งถึง: {to_email} | เรื่อง: {task['title']}")
                return True
    
    # รันฟังก์ชันตรวจสอบ + พิมพ์สถานะขึ้น Terminal
    run_notification_check(
        send_email_func=lambda t: send_email(t['email'], t),
        hours_ahead=24  # ดึงงานใน 24 ชม. ข้างหน้า (แก้ตัวเลขได้ตามต้องการ)
    )