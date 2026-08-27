from python.core.database import get_connection
from datetime import date


def get_meeting_list(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m.meeting_id,
                    m.meeting_name,
                    m.meeting_date,
                    v.venue_name,
                    m.performance_type,
                    m.official_url,
                    p.prefecture_name,

                    COALESCE(
                        u.is_join,
                        FALSE
                    ) AS is_join

                FROM m_meeting m

                LEFT JOIN m_venue v
                    ON m.venue_id = v.venue_id

                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code

                LEFT JOIN t_meeting_user u
                    ON m.meeting_id = u.meeting_id
                   AND u.user_id = %s

                WHERE
                    m.is_deleted = FALSE
                    AND m.public_flag = TRUE
                    AND m.meeting_date >= CURRENT_DATE

                ORDER BY
                    m.meeting_date ASC
                """,
                (user_id,)
            )

            meetings = cur.fetchall()

            for meeting in meetings:
                meeting["remaining_days"] = (
                    meeting["meeting_date"] - date.today()
                ).days

            return meetings

    finally:
        conn.close()
