from python.core.database import get_connection


def get_meeting_history_list(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m.meeting_id,
                    m.meeting_name,
                    m.meeting_date,
                    m.performance_type,
                    m.venue_name,
                    p.prefecture_name,

                    r.seat_info,
                    r.memo,

                    COALESCE(
                        SUM(e.amount),
                        0
                    ) AS total_expense

                FROM m_meeting m

                INNER JOIN t_meeting_user u
                    ON m.meeting_id = u.meeting_id

                LEFT JOIN m_prefecture p
                    ON m.prefecture_code = p.prefecture_code

                LEFT JOIN t_meeting_record r
                    ON m.meeting_id = r.meeting_id
                   AND r.user_id = u.user_id

                LEFT JOIN t_meeting_expense e
                    ON m.meeting_id = e.meeting_id
                   AND e.user_id = u.user_id

                WHERE
                    u.user_id = %s
                    AND u.is_join = TRUE
                    AND m.meeting_date < CURRENT_DATE
                    AND m.is_deleted = FALSE

                GROUP BY
                    m.meeting_id,
                    m.meeting_name,
                    m.meeting_date,
                    m.performance_type,
                    m.venue_name,
                    p.prefecture_name,
                    r.seat_info,
                    r.memo

                ORDER BY
                    m.meeting_date DESC
                """,
                (user_id,)
            )

            return cur.fetchall()

    finally:
        conn.close()
