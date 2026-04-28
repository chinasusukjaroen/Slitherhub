import sqlite3
#สร้าง DB 
def create_assignments_table():
    conn = None
    try:
        conn = sqlite3.connect("assignments.db")
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
                created_at       TIMESTAMP DEFAULT (datetime('now', 'localtime'))
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
#ดึงงานทุกงานออกมา
def get_assignments():
    conn = None
    try:
        conn = sqlite3.connect("assignment.db")
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