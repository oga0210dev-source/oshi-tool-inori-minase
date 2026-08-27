from python.core.database import get_connection
from datetime import date


def get_live_list(user_id):
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
                    COALESCE(u.is_join, FALSE) AS is_join
                FROM m_live l
                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id
                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code
                LEFT JOIN t_live_user u
                    ON l.live_id = u.live_id
                   AND u.user_id = %s
                WHERE
                    l.is_deleted = FALSE
                    AND l.public_flag = TRUE
                    AND l.live_date >= CURRENT_DATE
                ORDER BY
                    l.live_date ASC
                """,
                (user_id,)
            )

            lives = cur.fetchall()

            for live in lives:
                live["remaining_days"] = (
                    live["live_date"] - date.today()
                ).days

            return lives

    finally:
        conn.close()
