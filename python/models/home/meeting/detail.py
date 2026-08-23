from python.core.database import get_connection


def get_meeting_detail(user_id, meeting_id):
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
                    m.official_url,
                    COALESCE(u.is_join, FALSE) AS is_join
                FROM m_meeting m
                LEFT JOIN m_prefecture p
                    ON m.prefecture_code = p.prefecture_code
                LEFT JOIN t_meeting_user u
                    ON m.meeting_id = u.meeting_id
                   AND u.user_id = %s
                WHERE
                    m.meeting_id = %s
                    AND m.is_deleted = FALSE
                    AND m.public_flag = TRUE
                """,
                (
                    user_id,
                    meeting_id
                )
            )

            return cur.fetchone()

    finally:
        conn.close()


def get_meeting_guest_list(meeting_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    guest_id,
                    guest_name,
                    display_order
                FROM m_meeting_guest
                WHERE meeting_id = %s
                AND is_deleted = FALSE
                ORDER BY
                    display_order,
                    guest_id
                """,
                (
                    meeting_id,
                )
            )

            return cur.fetchall()

    finally:
        conn.close()
