import sqlite3
#สร้างDB
def create_users_table():
    conn = None
    try:
        conn = sqlite3.connect("users.db")
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
        if conn:
            conn.rollback()
        print("Error creating users table:", e)

    finally:
        if conn:
            conn.close()
#ดึงข้อมูลทุกคนออกมา
def get_users():
    conn = None
    try:
        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                user_id,
                student_id,
                username,
                display_name,
                email,
                moodle_user_id,
                line_user_id,
                is_line_notify_active,
                last_login,
                created_at
            FROM users
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        users = [dict(row) for row in rows]

        return {"success": True, "data": users, "total": len(users)}

    except Exception as e:
        return {"success": False, "data": [], "total": 0, "error": str(e)}

    finally:
        if conn:
            conn.close()

#ดึงข้อมูลออกมาตามid
def get_user_by_student_id(student_id: str):
    conn = None
    try:
        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE student_id = ?
        """, (student_id,))

        row = cursor.fetchone()

        if row is None:
            return {"success": False, "data": None, "error": "User not found"}

        return {"success": True, "data": dict(row)}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

    finally:
        if conn:
            conn.close()