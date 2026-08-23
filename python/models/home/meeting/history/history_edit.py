from python.core.database import get_connection


def get_meeting_record(user_id, meeting_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    record_id,
                    seat_info,
                    memo

                FROM t_meeting_record

                WHERE
                    user_id = %s
                    AND meeting_id = %s
                """,
                (
                    user_id,
                    meeting_id
                )
            )

            return cur.fetchone()

    finally:
        conn.close()


def save_meeting_record(
        user_id,
        meeting_id,
        seat_info,
        memo
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    record_id

                FROM t_meeting_record

                WHERE
                    user_id = %s
                    AND meeting_id = %s
                """,
                (
                    user_id,
                    meeting_id
                )
            )

            record = cur.fetchone()

            if record:
                cur.execute(
                    """
                    UPDATE t_meeting_record

                    SET
                        seat_info = %s,
                        memo = %s,
                        updated_at = CURRENT_TIMESTAMP

                    WHERE
                        user_id = %s
                        AND meeting_id = %s
                    """,
                    (
                        seat_info,
                        memo,
                        user_id,
                        meeting_id
                    )
                )

            else:
                cur.execute(
                    """
                    INSERT INTO t_meeting_record(
                        user_id,
                        meeting_id,
                        seat_info,
                        memo
                    )

                    VALUES(
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        user_id,
                        meeting_id,
                        seat_info,
                        memo
                    )
                )

            conn.commit()

    finally:
        conn.close()
