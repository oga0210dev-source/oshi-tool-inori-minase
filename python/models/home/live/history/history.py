from python.core.database import get_connection


def get_live_history_list(user_id):
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
                    p.prefecture_name,

                    r.seat_info,
                    r.memo,

                    COALESCE(
                        SUM(e.amount),
                        0
                    ) AS total_expense

                FROM m_live l

                INNER JOIN t_live_user u
                    ON l.live_id = u.live_id

                LEFT JOIN m_prefecture p
                    ON l.prefecture_code = p.prefecture_code

                LEFT JOIN t_live_record r
                    ON l.live_id = r.live_id
                   AND r.user_id = u.user_id

                LEFT JOIN t_live_expense e
                    ON l.live_id = e.live_id
                   AND e.user_id = u.user_id

                WHERE
                    u.user_id = %s
                    AND u.is_join = TRUE
                    AND l.live_date < CURRENT_DATE

                GROUP BY
                    l.live_id,
                    l.live_name,
                    l.tour_name,
                    l.live_date,
                    l.venue_name,
                    p.prefecture_name,
                    r.seat_info,
                    r.memo

                ORDER BY
                    l.live_date DESC
                """,
                (user_id,)
            )

            return cur.fetchall()

    finally:
        conn.close()
