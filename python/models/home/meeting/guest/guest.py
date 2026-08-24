from python.core.database import get_connection


def get_guest_list():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    MIN(g.guest_id) AS guest_id,
                    g.guest_name,
                    COUNT(*) AS appearance_count,
                    MAX(m.meeting_date) AS latest_meeting_date
                FROM m_meeting_guest g
                INNER JOIN m_meeting m
                    ON g.meeting_id = m.meeting_id
                WHERE
                    g.is_deleted = FALSE
                    AND m.is_deleted = FALSE
                    AND m.public_flag = TRUE
                GROUP BY
                    g.guest_name
                ORDER BY
                    appearance_count DESC,
                    g.guest_name ASC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()
