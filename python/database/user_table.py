from python.core.database import get_connection


def create_tables():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS M_USER(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            user_name TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            create_date TEXT NOT NULL,
            update_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
