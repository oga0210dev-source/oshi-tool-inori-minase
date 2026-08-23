from python.core.database import get_connection


def get_expense_type_list():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    expense_type_id,
                    expense_type_name
                FROM m_expense_type
                WHERE
                    is_public = TRUE
                ORDER BY
                    display_order
                """
            )

            return cur.fetchall()

    finally:
        conn.close()


def insert_expense(
        user_id,
        meeting_id,
        expense_type_id,
        amount,
        memo
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO t_meeting_expense(
                    user_id,
                    meeting_id,
                    expense_type_id,
                    amount,
                    memo
                )
                VALUES(
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    user_id,
                    meeting_id,
                    expense_type_id,
                    amount,
                    memo
                )
            )

            conn.commit()

    finally:
        conn.close()
