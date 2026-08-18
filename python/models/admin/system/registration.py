from python.core.database import get_connection


def get_registration_mode():
    """
    新規登録モード取得

    0: 登録停止
    1: 一般登録
    2: 招待制
    """
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    setting_value
                FROM m_system_setting
                WHERE setting_key = %s
                """,
                ("registration_mode",)
            )

            result = cur.fetchone()

            if not result:
                return "0"

            return result["setting_value"]

    finally:
        conn.close()


def update_registration_mode(registration_mode):
    """
    新規登録モード更新
    """
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_system_setting(
                    setting_key,
                    setting_value,
                    updated_at
                )
                VALUES(
                    %s,
                    %s,
                    CURRENT_TIMESTAMP
                )
                ON CONFLICT (setting_key)
                DO UPDATE SET
                    setting_value = EXCLUDED.setting_value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    "registration_mode",
                    registration_mode
                )
            )

        conn.commit()

    finally:
        conn.close()
