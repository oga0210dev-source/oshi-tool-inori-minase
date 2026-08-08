from python.core.database import get_connection


def delete_expense(
    user_id,
    expense_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM t_live_expense
                WHERE expense_id = %s
                AND user_id = %s
                """,
                (
                    expense_id,
                    user_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def get_live_id(
    user_id,
    expense_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT live_id
                FROM t_live_expense
                WHERE expense_id = %s
                AND user_id = %s
                """,
                (
                    expense_id,
                    user_id
                )
            )

            row = cur.fetchone()

            if row:
                return row["live_id"]

            return None

    finally:
        conn.close()
