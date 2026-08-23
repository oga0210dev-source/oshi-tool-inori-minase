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
                DELETE FROM t_meeting_expense
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


def get_meeting_id(
        user_id,
        expense_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    meeting_id

                FROM t_meeting_expense

                WHERE
                    expense_id = %s
                    AND user_id = %s
                """,
                (
                    expense_id,
                    user_id
                )
            )

            row = cur.fetchone()

            if row:
                return row["meeting_id"]

            return None

    finally:
        conn.close()
