from python.core.database import get_connection


def get_live_detail(user_id, live_id):
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
                    l.blu_ray_url,
                    l.official_url,
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
                    l.live_id = %s
                    AND l.is_deleted = FALSE
                    AND l.public_flag = TRUE
                """,
                (
                    user_id,
                    live_id
                )
            )

            return cur.fetchone()

    finally:
        conn.close()
