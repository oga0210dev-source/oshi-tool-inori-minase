from python.core.database import get_connection


def get_live_record(user_id, live_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    record_id,
                    seat_info,
                    memo

                FROM t_live_record

                WHERE
                    user_id = %s
                    AND live_id = %s
                """,
                (
                    user_id,
                    live_id
                )
            )

            return cur.fetchone()

    finally:
        conn.close()


def save_live_record(user_id, live_id, seat_info, memo):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    record_id

                FROM t_live_record

                WHERE
                    user_id = %s
                    AND live_id = %s
                """,
                (
                    user_id,
                    live_id
                )
            )

            record = cur.fetchone()

            if record:
                cur.execute(
                    """
                    UPDATE t_live_record

                    SET
                        seat_info = %s,
                        memo = %s,
                        updated_at = CURRENT_TIMESTAMP

                    WHERE
                        user_id = %s
                        AND live_id = %s
                    """,
                    (
                        seat_info,
                        memo,
                        user_id,
                        live_id
                    )
                )

            else:
                cur.execute(
                    """
                    INSERT INTO t_live_record(
                        user_id,
                        live_id,
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
                        live_id,
                        seat_info,
                        memo
                    )
                )

            conn.commit()

    finally:
        conn.close()
