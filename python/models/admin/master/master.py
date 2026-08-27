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


def get_venue_list():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    v.venue_id,
                    v.venue_name,
                    v.prefecture_code,
                    p.prefecture_name
                FROM m_venue v

                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code

                WHERE
                    v.is_deleted = FALSE

                ORDER BY
                    v.prefecture_code,
                    v.venue_name
            """)

            return cur.fetchall()

    finally:
        conn.close()
