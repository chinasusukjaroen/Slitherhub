# mock_add_assignment.py
from datetime import datetime, timedelta
from database import get_conn
from model.assignment_model import save_assignment  # 🔹 ปรับ path ถ้าไฟล์อยู่คนละที่

def mock_add_assignment():
    print("🔧 กำลังเพิ่มงานทดสอบลง database...")
    
    # 📦 สร้างข้อมูลงานทดสอบ
    now = datetime.now()
    uid = f"mock-assign-{int(now.timestamp())}"
    deadline = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🆔 UID: {uid}")
    print(f"📚 วิชา: CS101 — Intro to Programming")
    print(f"📝 ชื่อ: [MOCK] งานทดสอบเพิ่มลง DB")
    print(f"⏰ Deadline: {deadline}")
    print("-" * 40)
    
    # 📥 เรียกฟังก์ชันบันทึก (ปรับชื่อตามไฟล์จริงของคุณ)
    result = save_assignment(
        moodle_assignment_uid=uid,
        title="[MOCK] งานทดสอบเพิ่มลง DB",
        deadline=deadline,
        course_id="CS101",
        course_name="Intro to Programming",
        description="งานนี้ถูกสร้างจากสคริปต์ทดสอบแบบง่าย",
        source_url="https://moodle.example.com/test"
    )
    
    # ✅ เช็คผลลัพธ์
    if result.get("success"):
        print("✅ บันทึกสำเร็จ!")
        
        # 🔍 ดึงกลับมายืนยันใน DB
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT title, deadline FROM assignments WHERE moodle_assignment_uid = ?", (uid,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            print(f"🔍 ยืนยันใน database.db: '{row[0]}' | {row[1]}")
        else:
            print("⚠️ บันทึกสำเร็จแต่ไม่พบข้อมูลใน DB (เช็ค init_db() หรือตาราง assignments)")
        return True
    else:
        print(f"❌ บันทึกไม่สำเร็จ: {result.get('error')}")
        return False

if __name__ == "__main__":
    mock_add_assignment()