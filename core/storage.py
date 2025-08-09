# core/storage.py
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).parent.parent / "data" / "capsules.db"
FILES_PATH = Path(__file__).parent.parent / "data" / "capsule_files"

def init_db():
    FILES_PATH.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS capsules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            unlock_time TEXT,
            type TEXT,
            file_path TEXT,
            salt BLOB,
            nonce BLOB,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_capsule(title: str, unlock_time: datetime, capsule_type: str,
                 encrypted_data: bytes, nonce: bytes, salt: bytes):
    init_db()
    file_name = f"{title}_{int(unlock_time.timestamp())}.tccap"
    file_path = FILES_PATH / file_name
    with open(file_path, "wb") as f:
        f.write(encrypted_data)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO capsules (title, unlock_time, type, file_path, salt, nonce, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, unlock_time.isoformat(), capsule_type, str(file_path), salt, nonce, "locked"))
    conn.commit()
    conn.close()

def load_locked_capsules(before: datetime = None) -> List[Dict[str, Any]]:
    """
    Return list of capsules whose unlock_time <= before and status == 'locked'.
    If before is None, uses current time.
    """
    init_db()
    if before is None:
        before = datetime.now()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, unlock_time, type, file_path, salt, nonce
        FROM capsules
        WHERE status = 'locked' AND unlock_time <= ?
    """, (before.isoformat(),))
    rows = cur.fetchall()
    conn.close()

    capsules = []
    for r in rows:
        capsules.append({
            "id": r[0],
            "title": r[1],
            "unlock_time": datetime.fromisoformat(r[2]),
            "type": r[3],
            "file_path": r[4],
            "salt": r[5],
            "nonce": r[6],
        })
    return capsules

def read_encrypted_blob(file_path: str) -> bytes:
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Capsule file not found: {file_path}")
        return None

def mark_unlocked(capsule_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE capsules SET status = 'unlocked' WHERE id = ?", (capsule_id,))
    conn.commit()
    conn.close()

def check_capsules():
    """
    Check all capsules and print their status.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, unlock_time, status FROM capsules")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No capsules found.")
        return

    for r in rows:
        print(f"ID: {r[0]}, Title: {r[1]}, Unlock Time: {r[2]}, Status: {r[3]}")