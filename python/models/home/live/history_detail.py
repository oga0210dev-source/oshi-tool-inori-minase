from python.core.database import get_connection


def get_live_history_detail(user_id, live_id):
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
                    l.venue_name,
                    p.prefecture_name,

                    r.seat_info,
                    r.memo

                FROM m_live l

                LEFT JOIN m_prefecture p
                    ON l.prefecture_code = p.prefecture_code

                LEFT JOIN t_live_record r
                    ON l.live_id = r.live_id
                   AND r.user_id = %s

                WHERE
                    l.live_id = %s
                """,
                (
                    user_id,
                    live_id
                )
            )
            return cur.fetchone()
    finally:
        conn.close()


def get_live_expense_list(user_id, live_id):
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

                FROM t_live_expense e

                LEFT JOIN m_expense_type t
                    ON e.expense_type_id = t.expense_type_id

                WHERE
                    e.user_id = %s
                    AND e.live_id = %s

                ORDER BY
                    e.expense_id ASC
                """,
                (
                    user_id,
                    live_id
                )
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_total_expense(user_id, live_id):
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

                FROM t_live_expense

                WHERE
                    user_id = %s
                    AND live_id = %s
                """,
                (
                    user_id,
                    live_id
                )
            )
            row = cur.fetchone()

            return row["coalesce"] if row else 0
    finally:
        conn.close()
