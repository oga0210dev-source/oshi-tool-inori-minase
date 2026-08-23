from python.core.database import get_connection


def get_expense(
        user_id,
        expense_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    t.expense_id,
                    t.meeting_id,
                    t.expense_type_id,
                    t.memo,
                    t.amount
                FROM t_meeting_expense t
                WHERE
                    t.expense_id = %s
                    AND t.user_id = %s
                """,
                (
                    expense_id,
                    user_id
                )
            )

            return cur.fetchone()

    finally:
        conn.close()


def update_expense(
        user_id,
        expense_id,
        expense_type_id,
        memo,
        amount
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE t_meeting_expense
                SET
                    expense_type_id = %s,
                    memo = %s,
                    amount = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    expense_id = %s
                    AND user_id = %s
                """,
                (
                    expense_type_id,
                    memo,
                    amount,
                    expense_id,
                    user_id
                )
            )

        conn.commit()

    finally:
        conn.close()
