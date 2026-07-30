from python.core.database import get_connection


class PublicSettingModel:

    @staticmethod
    def get(user_id):
        """
        公開設定取得
        """
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        user_id,
                        gender_public,
                        birthday_public,
                        age_public,
                        member_since_public,
                        prefecture_public,
                        sns_public,
                        live_public,
                        meeting_public
                    FROM m_user_public_setting
                    WHERE user_id = %s
                    """,
                    (user_id,)
                )

                return cur.fetchone()

        finally:
            conn.close()

    @staticmethod
    def create(user_id):
        """
        公開設定初期登録
        """
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO m_user_public_setting (
                        user_id
                    )
                    VALUES (%s)
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    (user_id,)
                )

            conn.commit()

        finally:
            conn.close()

    @staticmethod
    def update(
            user_id,
            gender_public,
            birthday_public,
            age_public,
            member_since_public,
            prefecture_public,
            sns_public,
            live_public,
            meeting_public
    ):
        """
        公開設定更新
        """
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE m_user_public_setting
                    SET
                        gender_public = %s,
                        birthday_public = %s,
                        age_public = %s,
                        member_since_public = %s,
                        prefecture_public = %s,
                        sns_public = %s,
                        live_public = %s,
                        meeting_public = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                    """,
                    (
                        gender_public,
                        birthday_public,
                        age_public,
                        member_since_public,
                        prefecture_public,
                        sns_public,
                        live_public,
                        meeting_public,
                        user_id
                    )
                )

            conn.commit()

        finally:
            conn.close()
