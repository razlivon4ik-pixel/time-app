from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Office Time Tracking")

def init_db():
    conn = sqlite3.connect("office_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            password TEXT,
            fullname TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            date TEXT,
            status TEXT,
            hours REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class LogSchema(BaseModel):
    emp_id: str
    password: str
    date: str
    status: str
    hours: float

@app.post("/api/submit_time")
def submit_time(data: LogSchema):
    conn = sqlite3.connect("office_data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT fullname FROM employees WHERE emp_id = ? AND password = ?", (data.emp_id, data.password))
    employee = cursor.fetchone()
    
    if not employee:
        conn.close()
        raise HTTPException(status_code=401, detail="Błędny identyfikator (ID) lub hasło!")
    
    fullname = employee[0]
    
    cursor.execute("SELECT id FROM time_logs WHERE emp_id = ? AND date = ?", (data.emp_id, data.date))
    already_exists = cursor.fetchone()
    
    if already_exists:
        cursor.execute(
            "UPDATE time_logs SET status = ?, hours = ? WHERE emp_id = ? AND date = ?",
            (data.status, data.hours, data.emp_id, data.date)
        )
        msg = f"Dane za dzień {data.date} zostały pomyślnie zaktualizowane dla: {fullname}"
    else:
        cursor.execute(
            "INSERT INTO time_logs (emp_id, date, status, hours) VALUES (?, ?, ?, ?)",
            (data.emp_id, data.date, data.status, data.hours)
        )
        msg = f"Dane za dzień {data.date} zostały pomyślnie zapisane dla: {fullname}"
        
    conn.commit()
    conn.close()
    return {"status": "success", "message": msg}