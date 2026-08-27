from python.core.database import get_connection


def get_meeting_history_detail(user_id, meeting_id):
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
                    v.venue_name,
                    p.prefecture_name,

                    r.seat_info,
                    r.memo

                FROM m_meeting m

                LEFT JOIN m_venue v
                    ON m.venue_id = v.venue_id

                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code

                LEFT JOIN t_meeting_record r
                    ON m.meeting_id = r.meeting_id
                   AND r.user_id = %s

                WHERE
                    m.meeting_id = %s
                    AND m.is_deleted = FALSE
                """,
                (
                    user_id,
                    meeting_id
                )
            )

            return cur.fetchone()

    finally:
        conn.close()


def get_meeting_expense_list(user_id, meeting_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    e.expense_id,
                    e.amount,
                    e.memo,
                    t.expense_type_name

                FROM t_meeting_expense e

                LEFT JOIN m_expense_type t
                    ON e.expense_type_id = t.expense_type_id

                WHERE
                    e.user_id = %s
                    AND e.meeting_id = %s

                ORDER BY
                    e.expense_id ASC
                """,
                (
                    user_id,
                    meeting_id
                )
            )

            return cur.fetchall()


    finally:
        conn.close()


def get_total_expense(user_id, meeting_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COALESCE(
                        SUM(amount),
                        0
                    )

                FROM t_meeting_expense

                WHERE
                    user_id = %s
                    AND meeting_id = %s
                """,
                (
                    user_id,
                    meeting_id
                )
            )

            row = cur.fetchone()

            return row["coalesce"] if row else 0

    finally:
        conn.close()
