from python.core.database import get_connection


def get_meeting_archive_list(user_id, keyword=None, sort="new"):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            sql = """
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
                    m.is_deleted = FALSE
                    AND m.public_flag = TRUE
            """

            params = [user_id]

            if keyword:
                sql += """
                    AND (
                        m.meeting_name ILIKE %s
                        OR m.venue_name ILIKE %s
                        OR p.prefecture_name ILIKE %s
                    )
                """
                keyword = f"%{keyword}%"
                params.extend([keyword, keyword, keyword])

            if sort == "old":
                sql += " ORDER BY m.meeting_date ASC"
            elif sort == "name":
                sql += " ORDER BY m.meeting_name ASC"
            else:
                sql += " ORDER BY m.meeting_date DESC"

            cur.execute(sql, params)
            return cur.fetchall()

    finally:
        conn.close()


def join_meeting(user_id, meeting_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO t_meeting_user
                (user_id, meeting_id, is_join)
                VALUES (%s, %s, TRUE)
                ON CONFLICT(user_id, meeting_id)
                DO UPDATE SET is_join = TRUE
                """,
                (user_id, meeting_id)
            )

        conn.commit()

    finally:
        conn.close()


def cancel_join(user_id, meeting_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE t_meeting_user
                SET is_join = FALSE
                WHERE user_id = %s
                  AND meeting_id = %s
                """,
                (user_id, meeting_id)
            )

        conn.commit()

    finally:
        conn.close()
