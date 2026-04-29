import sqlite3
from database import get_conn

def create_assignments_table():
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                assignment_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                moodle_assignment_uid TEXT UNIQUE NOT NULL,
                course_id             TEXT,
                course_name           TEXT,
                title                 TEXT NOT NULL,
                description           TEXT,
                source_url            TEXT,
                deadline              DATETIME NOT NULL,
                is_notified           BOOLEAN DEFAULT 0,
                notified_at           TIMESTAMP,
                created_at            TIMESTAMP DEFAULT (datetime('now', 'localtime'))
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


def get_assignments():
    conn = None
    try:
        conn = get_conn()  # ← แก้
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
                is_notified,
                notified_at,
                created_at
            FROM assignments
            ORDER BY deadline ASC
        """)

        assignments = [dict(row) for row in cursor.fetchall()]
        return {"success": True, "data": assignments, "total": len(assignments)}

    except Exception as e:
        return {"success": False, "data": [], "total": 0, "error": str(e)}

    finally:
        if conn:
            conn.close()


def save_assignment(moodle_assignment_uid, title, deadline,
                    course_id=None, course_name=None,
                    description=None, source_url=None):
    conn = None
    try:
        conn = get_conn()  # ← แก้

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assignments 
                (moodle_assignment_uid, course_id, course_name, 
                 title, description, source_url, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(moodle_assignment_uid) DO UPDATE SET
                course_id   = excluded.course_id,
                course_name = excluded.course_name,
                title       = excluded.title,
                description = excluded.description,
                source_url  = excluded.source_url,
                deadline    = excluded.deadline
        """, (moodle_assignment_uid, course_id, course_name,
              title, description, source_url, deadline))

        conn.commit()
        return {"success": True, "assignment_id": cursor.lastrowid}

    except Exception as e:
        if conn:
            conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        if conn:
            conn.close()