from python.core.database import get_connection


def get_live_history_detail(user_id, live_id):
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
                    v.venue_name,
                    p.prefecture_name,

                    r.seat_info,
                    r.memo

                FROM m_live l

                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id

                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code

                LEFT JOIN t_live_record r
                    ON l.live_id = r.live_id
                   AND r.user_id = %s

                WHERE
                    l.live_id = %s
                """,
                (
                    user_id,
                    live_id
                )
            )
            return cur.fetchone()
    finally:
        conn.close()
