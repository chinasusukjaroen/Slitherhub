import sqlite3
from database import get_conn 
#สร้าง DB 
def create_assignments_table():
    conn = None
    try:
        conn = conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                assignment_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                moodle_assignment_uid TEXT UNIQUE NOT NULL,
                course_id        TEXT,
                course_name      TEXT,
                title            TEXT NOT NULL,
                description      TEXT,
                source_url       TEXT,
                deadline         DATETIME NOT NULL,
                created_at       TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                is_notified      BOOLEAN DEFAULT 0
            )
        """)

        conn.commit()
        print("Table 'assignments' created successfully")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Error creating table:", e)

    finally:
        if conn:
            conn.close()

def save_assignment(moodle_assignment_uid, title, deadline,
                    course_id=None, course_name=None,
                    description=None, source_url=None):
    try:
        conn = get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print(f"[DEBUG] กำลังบันทึก: {moodle_assignment_uid}")

        cursor.execute("""
            INSERT OR IGNORE INTO assignments
            (moodle_assignment_uid, course_id, course_name, title, description, source_url, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (moodle_assignment_uid, course_id, course_name, title, description, source_url, deadline))
        
        conn.commit()
        print("[DEBUG] Commit สำเร็จ!")
        
        cursor.execute("SELECT assignment_id FROM assignments WHERE moodle_assignment_uid = ?", (moodle_assignment_uid,))
        row = cursor.fetchone()

        print("Assignment:", row[0])

        return {"success": True, "data": row[0] if row else None}

    except Exception as e:
        print(f"[DEBUG] ERROR: {type(e).__name__}: {e}")
        return {"success": False, "data": None, "error": str(e)}
    finally:
        conn.close()

def update_assignment_deadline_and_description(moodle_assignemnt_uid, deadline, description):
    if deadline is None or description is None: return
    conn = None
    try:
        conn = get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE assignments
            SET deadline = ?, description = ?
            WHERE moodle_assignment_uid = ?
            AND (
                    deadline IS NULL OR deadline != ?
                OR description IS NULL OR description != ?
            )
        """, (deadline, description, moodle_assignemnt_uid, deadline, description))

        updated = cursor.rowcount > 0

        cursor.execute("""
            SELECT assignment_id
            FROM assignments
            WHERE moodle_assignment_uid = ?
        """, (moodle_assignemnt_uid,))

        row = cursor.fetchone()

        return {"success": True, "updated": updated, "data": row[0] if row else None}

    finally:
        if conn: conn.close()

#ดึงงานทุกงานออกมา
def get_assignments():
    conn = None
    try:
        conn = get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                assignment_id,
                moodle_assignment_uid,
                course_id,
                course_name,
                title,
                description,
                source_url,
                deadline,
                created_at
            FROM assignments
            ORDER BY deadline ASC
        """)

        rows = cursor.fetchall()
        assignments = [dict(row) for row in rows]

        return {"success": True, "data": assignments, "total": len(assignments)}

    except Exception as e:
        return {"success": False, "data": [], "total": 0, "error": str(e)}

    finally:
        if conn:
            conn.close()

def get_assignment_by_assignment_id(assignment_id):
    conn = None
    try:
        conn = get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                assignment_id,
                moodle_assignment_uid,
                course_id,
                course_name,
                title,
                description,
                source_url,
                deadline,
                created_at
            FROM assignments
            WHERE assignment_id = ?
        """, (assignment_id,))

        row = cursor.fetchone()


        return {"success": True, "data": dict(row) if row else None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

    finally:
        if conn:
            conn.close()


def get_assignment_by_moodle_id(moodle_id):
    conn = None
    try:
        conn = get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                assignment_id,
                moodle_assignment_uid,
                course_id,
                course_name,
                title,
                description,
                source_url,
                deadline,
                created_at
            FROM assignments
            WHERE moodle_assignment_uid = ?
        """, (moodle_id,))

        row = cursor.fetchone()


        return {"success": True, "data": dict(row) if row else None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

    finally:
        if conn:
            conn.close()