from datetime import datetime

from python.core.database import get_connection


class UserModel:

    @staticmethod
    def exists_user_id(user_id: str) -> bool:
        """ユーザーIDが存在するか"""

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1
            FROM M_USER
            WHERE USER_ID = ?
        """, (user_id,))

        result = cursor.fetchone()

        conn.close()

        return result is not None

    @staticmethod
    def create_user(
            user_id: str,
            user_name: str,
            password: str,
            role: str
    ) -> None:
        """ユーザー登録"""

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO M_USER
            (
                USER_ID,
                USER_NAME,
                PASSWORD,
                ROLE,
                CREATE_DATE,
                UPDATE_DATE
            )
            VALUES
            (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_name,
            password,
            role,
            datetime.now(),
            datetime.now()
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def get_user(user_id: str):
        """ユーザー取得"""

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM M_USER
            WHERE USER_ID = ?
        """, (user_id,))

        user = cursor.fetchone()

        conn.close()

        return user
