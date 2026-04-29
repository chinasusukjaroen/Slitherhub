import sqlite3
from database import get_conn 
#สร้างDB
def create_user_tasks_table():
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tasks (
                user_task_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                assignment_id INTEGER NOT NULL,
                status        TEXT DEFAULT 'pending'
                              CHECK(status IN ('pending', 'submitted', 'graded', 'overdue')),
                is_notified   BOOLEAN DEFAULT 0,
                last_sync_at  TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id)       REFERENCES users(user_id),
                FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
                UNIQUE(user_id, assignment_id)
            )
        """)

        conn.commit()
        print("Table 'user_tasks' created successfully")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        conn.close()
#เบื้องต้นดึงtaskทั้งหมดของทุกคน
def get_user_tasks():
    conn = None
    try:
        conn = sqlite3.connect("user_tasks.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                user_task_id,
                user_id,
                assignment_id,
                status,
                is_notified,
                last_sync_at
            FROM user_tasks
            ORDER BY last_sync_at DESC
        """)

        rows = cursor.fetchall()
        tasks = [dict(row) for row in rows]

        return {"success": True, "data": tasks, "total": len(tasks)}

    except Exception as e:
        return {"success": False, "data": [], "total": 0, "error": str(e)}

    finally:
        if conn:
            conn.close()

#เบื้องต้นดึง task ทั้งหมดของนักศึกษา 1 คน ตาม id
def get_user_tasks_by_user_id(user_id: int):
    conn = None
    try:
        conn = sqlite3.connect("user_tasks.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                user_task_id,
                user_id,
                assignment_id,
                status,
                is_notified,
                last_sync_at
            FROM user_tasks
            WHERE user_id = ?
            ORDER BY last_sync_at DESC
        """, (user_id,))

        rows = cursor.fetchall()
        tasks = [dict(row) for row in rows]

        return {"success": True, "data": tasks, "total": len(tasks)}

    except Exception as e:
        return {"success": False, "data": [], "total": 0, "error": str(e)}

    finally:
        if conn:
            conn.close()