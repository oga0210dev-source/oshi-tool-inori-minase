from python.core.database import get_connection


class UserSettingModel:

    @staticmethod
    def get_user_setting(user_id: str):
        """ユーザー設定を取得"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    user_id,
                    font_id
                FROM m_user_setting
                WHERE user_id = %s
            """, (user_id,))

            return cursor.fetchone()

        finally:
            conn.close()

    @staticmethod
    def get_font_id(user_id: str):
        """ユーザーのフォント設定を取得"""

        setting = UserSettingModel.get_user_setting(user_id)

        if not setting:
            return None

        return setting["font_id"]

    @staticmethod
    def update_font_id(user_id: str, font_id: str):
        """ユーザーのフォント設定を更新"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO m_user_setting
                (
                    user_id,
                    font_id
                )
                VALUES
                (
                    %s,
                    %s
                )
                ON CONFLICT (user_id)
                DO UPDATE SET
                    font_id = EXCLUDED.font_id
            """, (
                user_id,
                font_id
            ))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()
