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
                    m.venue_name,
                    m.performance_type,
                    m.official_url,
                    p.prefecture_name,
                    FALSE AS is_join
                FROM m_meeting m
                LEFT JOIN m_prefecture p
                    ON m.prefecture_code = p.prefecture_code
                WHERE
                    m.is_deleted = FALSE
                    AND m.public_flag = TRUE
                    AND m.meeting_date >= CURRENT_DATE
                ORDER BY
                    m.meeting_date ASC
                """
            )

            meetings = cur.fetchall()

            for meeting in meetings:
                meeting["remaining_days"] = (
                    meeting["meeting_date"] - date.today()
                ).days

            return meetings

    finally:
        conn.close()
