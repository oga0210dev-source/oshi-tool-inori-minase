from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE = BASE_DIR / "app.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
