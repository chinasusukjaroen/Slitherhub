import sqlite3
import os
from config import DB_PATH


def get_conn():
    """สร้าง Database Connection"""

    conn = sqlite3.connect(DB_PATH)
    
    conn.row_factory = sqlite3.Row

    # print("DB_PATH:", DB_PATH)
    # print("DB EXISTS:", os.path.exists(DB_PATH))
    # print("DB ABSOLUTE:", os.path.abspath(DB_PATH))

    return conn


def init_db():
    """สร้างตารางทั้งหมด"""
    from model.user_model import create_users_table
    from model.assignment_model import create_assignments_table
    from model.user_task_model import create_user_tasks_table

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL;")
    row = cursor.fetchone()

    print(dict(row))
    print("DB_PATH:", DB_PATH)

    create_users_table()
    create_assignments_table()
    create_user_tasks_table()


    conn.commit()
    conn.close()