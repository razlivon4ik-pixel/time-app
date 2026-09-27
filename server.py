from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

REAL_EMPLOYEES = [
    ('DL01', 'x9A2b4', 'David Lyszkowicz'),
    ('ER02', 'm5K7r3', 'Eldar Rajabov'),
    ('IS03', 'v3N8p1', 'Igor Sukhovii'),
    ('OS04', 't6B2w9', 'Oleksandr Stelmach'),
    ('PS05', 'c4R7x2', 'Pavlo Shulha'),
    ('LA06', 'z1M9k4', 'Luka Asanidze'),
    ('SM07', 'f5T3g8', 'Serhii Mestorenko'),
    ('SB08', 'q2W7e4', 'Subota Bogdan'),
    ('BK09', 'h8Y3j1', 'Bochram Kadurov'),
    ('SN10', 'p4K9l2', 'Serhii Narusevich'),
    ('OT11', 'r7V3c5', 'Oleksandr Tabota'),
    ('SP12', 'g2X8n3', 'Stanislaw Pohodnia'),
    ('GA13', 'b5M1s7', 'Giga Arveladze'),
    ('AB14', 'w9C4v2', 'Artem Babivskyi'),
    ('VN15', 'k3Z7d9', 'Vadim Novik'),
    ('MH16', 'e6F2t8', 'Mateusz Hucaluk'),
    ('SG17', 'j4Q9w1', 'Sorokopud Genadii'),
    ('BK18', 'n8V3m5', 'Belov Konstantin'),
    ('AK19', 't2Y7x4', 'Andrii Khomenko'),
    ('AP20', 'c5B1k9', 'Andrii Prasol'),
    ('AM21', 'z6R3p8', 'Artem Marochkin')
]

# Автоматичне створення та заповнення бази даних при запуску сервера
def init_db():
    conn = sqlite3.connect("office_data.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS employees (emp_id TEXT PRIMARY KEY, password TEXT, fullname TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS time_logs (emp_id TEXT, fullname TEXT, date TEXT, status TEXT, hours REAL)")
    
    # Перевіряємо, чи база пуста, якщо так - додаємо людей
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO employees VALUES (?, ?, ?)", REAL_EMPLOYEES)
        print("Базу працівників успішно заповнено автоматично!")
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
    
    # Валідація користувача (великі літери)
    cursor.execute("SELECT fullname FROM employees WHERE emp_id = ? AND password = ?", (data.emp_id.upper(), data.password))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=400, detail="Błędny identyfikator (ID) lub hasło!")
    
    fullname = user[0]
    
    # Зберігаємо звіт робочого часу
    cursor.execute("INSERT INTO time_logs VALUES (?, ?, ?, ?, ?)", 
                   (data.emp_id.upper(), fullname, data.date, data.status, data.hours))
    conn.commit()
    conn.close()
    
    return {"message": f"Dane za dzień {data.date} zostały pomyślnie zapisane dla: {fullname}"}

@app.get("/")
def read_root():
    return {"status": "working", "database": "initialized"}
