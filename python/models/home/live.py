from python.core.database import get_connection


def get_live_list():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    l.live_id,
                    l.live_name,
                    l.tour_name,
                    l.live_date,
                    l.venue_name,
                    p.prefecture_name
                FROM m_live l
                LEFT JOIN m_prefecture p
                ON l.prefecture_code = p.prefecture_code
                WHERE
                    l.is_deleted = FALSE
                    AND l.public_flag = TRUE
                    AND l.live_date >= CURRENT_DATE
                ORDER BY
                    l.live_date ASC
                LIMIT 1
                """
            )

            return cur.fetchall()

    finally:
        conn.close()
