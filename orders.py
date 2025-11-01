# orders.py
import sqlite3
from typing import List, Tuple

DB = "orders.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                isbn TEXT,
                title TEXT,
                address TEXT,
                status TEXT DEFAULT 'Pending',
                tracking TEXT
            )
        """)

def create_order(user_id: str, isbn: str, title: str, address: str) -> int:
    try:
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO orders (user_id, isbn, title, address) VALUES (?, ?, ?, ?)",
                (user_id, isbn, title, address)
            )
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        print(f"ERROR:orders:Order creation failed: {e}")
        return None

def get_orders() -> List[Tuple]:
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders")
        return cur.fetchall()

# Init on import
init_db()