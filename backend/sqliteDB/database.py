import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
def init_db():
    
    conn = sqlite3.connect("slither.db")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            course_Id TEXT PRIMARY KEY,
            course_Name TEXT NOT NULL,
            credit INTEGER DEFAULT 3
        )
    ''')

    # สร้างตาราง Assignments พร้อม Composite Primary Key
    cur.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            assignment_Name TEXT,
            course_Id TEXT,
            score REAL,
            status TEXT CHECK(status IN ('passed', 'late', 'unsent')),
            deadline TEXT,
            priority INTEGER,
            PRIMARY KEY (assignment_Name, course_Id),
            FOREIGN KEY (course_Id) REFERENCES subjects (course_Id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route("/add_course",methods=["POST"])
def add_course():
    data = request.json
    
    conn = sqlite3.connect("slither.db")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("""
        INSERT INTO subjects (course_Id, course_Name)
        VALUES (?, ?)
    """, (
    data["course_Id"],
    data["course_Name"]
    ))      
    conn.commit()
    conn.close()
    return jsonify({"status": "added"})
@app.route("/add_assignment",methods=["POST"])
def add_assignment():
    data = request.json
    
    conn = sqlite3.connect("slither.db")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    cur.execute("""
            INSERT INTO assignments (assignment_Name, course_Id, score, status, deadline, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["assignment_Name"],
            data["course_Id"],
            data["score"],
            data["status"],
            data["deadline"],
            data["priority"]
        ))
    conn.commit()
    conn.close()
    return jsonify({"status": "added"})
    
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8888)

