from python.core.database import get_connection


def get_live_archive_list(user_id, keyword=None, sort="new"):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            sql = """
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
            """

            params = [user_id]

            if keyword:
                sql += """
                    AND (
                        l.live_name ILIKE %s
                        OR l.tour_name ILIKE %s
                        OR v.venue_name ILIKE %s
                        OR p.prefecture_name ILIKE %s
                    )
                """

                keyword = f"%{keyword}%"

                params.extend([
                    keyword,
                    keyword,
                    keyword,
                    keyword
                ])

            if sort == "old":
                sql += """
                    ORDER BY
                        l.live_date ASC
                """

            elif sort == "tour":
                sql += """
                    ORDER BY
                        l.tour_name ASC,
                        l.live_date ASC
                """

            elif sort == "name":
                sql += """
                    ORDER BY
                        l.live_name ASC
                """

            else:
                sql += """
                    ORDER BY
                        l.live_date DESC
                """

            cur.execute(
                sql,
                params
            )

            return cur.fetchall()

    finally:
        conn.close()


def join_live(user_id, live_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO t_live_user
                (
                    user_id,
                    live_id,
                    is_join
                )
                VALUES
                (
                    %s,
                    %s,
                    TRUE
                )
                ON CONFLICT(user_id, live_id)
                DO UPDATE SET
                    is_join = TRUE
                """,
                (
                    user_id,
                    live_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def cancel_join(user_id, live_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE t_live_user
                SET is_join = FALSE
                WHERE
                    user_id = %s
                    AND live_id = %s
                """,
                (
                    user_id,
                    live_id
                )
            )

        conn.commit()

    finally:
        conn.close()
