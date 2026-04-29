import sqlite3
from database import get_conn 

# ─── สร้างตาราง ─────────────────────────────────────────────
def create_users_table():
    conn = None
    try:
        conn = get_conn()  # ✅ ใช้ตัวกลาง
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id               INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id            TEXT UNIQUE NOT NULL,
                username              TEXT,
                display_name          TEXT,
                email                 TEXT UNIQUE,
                moodle_API            TEXT,
                moodle_user_id        TEXT,
                line_user_id          TEXT,
                is_line_notify_active BOOLEAN DEFAULT 0,
                last_login            TIMESTAMP,
                created_at            TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        """)
        conn.commit()
        print("Table 'users' created successfully")
    except Exception as e:
        if conn: conn.rollback()
        print("Error creating users table:", e)
    finally:
        if conn: conn.close()

# ─── ดึงข้อมูลทุกคน ──────────────────────────────────────────
def get_users():
    conn = None
    try:
        conn = get_conn()  # ✅ แก้ตรงนี้
        # get_conn() ใน database.py ควรตั้ง row_factory ไว้แล้ว หากยังไม่มีให้เพิ่ม conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, student_id, username, display_name, email,
                   moodle_user_id, line_user_id, is_line_notify_active,
                   last_login, created_at
            FROM users ORDER BY created_at DESC
        """)
        users = [dict(row) for row in cursor.fetchall()]
        return {"success": True, "data": users, "total": len(users)}
    except Exception as e:
        return {"success": False, "data": [], "total": 0, "error": str(e)}
    finally:
        if conn: conn.close()

# ─── ดึงข้อมูลตาม student_id ─────────────────────────────────
def get_user_by_student_id(student_id: str):
    conn = None
    try:
        conn = get_conn()  # ✅ แก้ตรงนี้
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        
        if row is None:
            return {"success": False, "data": None, "error": "User not found"}
        return {"success": True, "data": dict(row)}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}
    finally:
        if conn: conn.close()

# ─── บันทึก/อัปเดตผู้ใช้ (UPSERT) ────────────────────────────
def save_user(student_id, username=None, display_name=None, email=None,
              moodle_API=None, moodle_user_id=None):
    conn = None
    try:
        conn = get_conn()  # ✅ แก้ตรงนี้
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users 
            (student_id, username, display_name, email, moodle_API, moodle_user_id, last_login)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            ON CONFLICT(student_id) DO UPDATE SET
                username = excluded.username,
                display_name = excluded.display_name,
                email = excluded.email,
                moodle_API = excluded.moodle_API,
                moodle_user_id = excluded.moodle_user_id,
                last_login = datetime('now', 'localtime')
        """, (student_id, username, display_name, email, moodle_API, moodle_user_id))
        conn.commit()

        conn.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM users WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        return {"success": True, "data": dict(row) if row else None}
    except Exception as e:
        if conn: conn.rollback()
        return {"success": False, "data": None, "error": str(e)}
    finally:
        if conn: conn.close()