from python.core.database import get_connection


def get_guest_detail(guest_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    g.guest_id,
                    g.guest_name,
                    COUNT(*) AS appearance_count,
                    MAX(m.meeting_date) AS latest_meeting_date
                FROM m_meeting_guest g
                INNER JOIN m_meeting m
                    ON g.meeting_id = m.meeting_id
                WHERE
                    g.guest_id = %s
                    AND g.is_deleted = FALSE
                    AND m.is_deleted = FALSE
                    AND m.public_flag = TRUE
                GROUP BY
                    g.guest_id,
                    g.guest_name
                """,
                (guest_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def get_guest_meeting_list(guest_name):
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
                    p.prefecture_name
                FROM m_meeting_guest g
                INNER JOIN m_meeting m
                    ON g.meeting_id = m.meeting_id
                LEFT JOIN m_prefecture p
                    ON m.prefecture_code = p.prefecture_code
                WHERE
                    g.guest_name = %s
                    AND g.is_deleted = FALSE
                    AND m.is_deleted = FALSE
                    AND m.public_flag = TRUE
                ORDER BY
                    m.meeting_date DESC,
                    m.meeting_id DESC
                """,
                (guest_name,)
            )

            return cur.fetchall()

    finally:
        conn.close()
