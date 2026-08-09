from python.core.database import get_connection


def get_lost_item_list(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    user_lost_item_id,
                    lost_item_id,
                    item_name,
                    is_checked
                FROM t_user_lost_item
                WHERE user_id = %s
                ORDER BY
                    CASE
                        WHEN lost_item_id IS NOT NULL THEN 0
                        ELSE 1
                    END,
                    user_lost_item_id ASC
                """,
                (user_id,)
            )

            return cur.fetchall()

    finally:
        conn.close()


def initialize_lost_items(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM t_user_lost_item
                    WHERE user_id = %s
                )
                """,
                (user_id,)
            )

            exists = cur.fetchone()["exists"]

            if exists:
                return

            cur.execute(
                """
                INSERT INTO t_user_lost_item (
                    user_id,
                    lost_item_id,
                    item_name,
                    is_checked
                )
                SELECT
                    %s,
                    lost_item_id,
                    item_name,
                    FALSE
                FROM m_lost_item
                WHERE is_deleted = FALSE
                ORDER BY display_order ASC, lost_item_id ASC
                """,
                (user_id,)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def update_lost_item_check(user_id, user_lost_item_id, is_checked):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE t_user_lost_item
                SET
                    is_checked = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_lost_item_id = %s
                  AND user_id = %s
                """,
                (
                    is_checked,
                    user_lost_item_id,
                    user_id
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def add_lost_item(user_id, item_name):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO t_user_lost_item (
                    user_id,
                    lost_item_id,
                    item_name,
                    is_checked
                )
                VALUES (
                    %s,
                    NULL,
                    %s,
                    FALSE
                )
                RETURNING user_lost_item_id
                """,
                (
                    user_id,
                    item_name
                )
            )

            user_lost_item_id = cur.fetchone()["user_lost_item_id"]

        conn.commit()
        return user_lost_item_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def update_lost_item(user_id, user_lost_item_id, item_name):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE t_user_lost_item
                SET
                    item_name = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_lost_item_id = %s
                  AND user_id = %s
                  AND lost_item_id IS NULL
                """,
                (
                    item_name,
                    user_lost_item_id,
                    user_id
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def delete_lost_item(user_id, user_lost_item_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM t_user_lost_item
                WHERE user_lost_item_id = %s
                  AND user_id = %s
                  AND lost_item_id IS NULL
                """,
                (
                    user_lost_item_id,
                    user_id
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def reset_lost_items(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE t_user_lost_item
                SET
                    is_checked = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """,
                (user_id,)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
