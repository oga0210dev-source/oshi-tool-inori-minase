from python.core.database import get_connection


def get_prefecture_list():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    prefecture_code,
                    prefecture_name,
                    area_name
                FROM m_prefecture
                WHERE is_active = TRUE
                ORDER BY display_order
            """)

            return cur.fetchall()

    finally:
        conn.close()
