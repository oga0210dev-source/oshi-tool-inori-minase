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
            WHERE USER_ID = %s
        """, (user_id,))

        result = cursor.fetchone()

        conn.close()

        return result is not None

    @staticmethod
    def create_user(
        user_id: str,
        user_name: str,
        password: str
    ) -> None:
        """ユーザー登録"""

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO M_USER
            (
                USER_ID,
                USER_NAME,
                PASSWORD
            )
            VALUES
            (%s, %s, %s)
        """, (
            user_id,
            user_name,
            password
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def get_user(user_id: str):
        """ユーザー取得"""

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                U.*,
                P.PREFECTURE_NAME
            FROM M_USER U
            LEFT JOIN M_PREFECTURE P
                ON U.PREFECTURE = P.PREFECTURE_CODE
            WHERE
                U.USER_ID=%s
            AND U.IS_ACTIVE=TRUE
        """, (user_id,))

        user = cursor.fetchone()

        conn.close()

        return user

    @staticmethod
    def update_user(
        user_id: str,
        user_name: str,
        member_since,
        email: str,
        gender: str,
        birthday,
        prefecture: int,
        x_account: str,
        instagram_account: str,
        discord_account: str,
        profile_message: str,
        profile_image: str = None
    ):
        """ユーザー情報更新"""

        conn = get_connection()
        cursor = conn.cursor()

        if profile_image:
            cursor.execute("""
                UPDATE M_USER
                SET
                    USER_NAME = %s,
                    MEMBER_SINCE = %s,
                    EMAIL = %s,
                    GENDER = %s,
                    BIRTHDAY = %s,
                    PREFECTURE = %s,
                    X_ACCOUNT = %s,
                    INSTAGRAM_ACCOUNT = %s,
                    DISCORD_ACCOUNT = %s,
                    PROFILE_MESSAGE = %s,
                    PROFILE_IMAGE = %s
                WHERE USER_ID = %s
            """, (
                user_name,
                member_since,
                email,
                gender,
                birthday,
                prefecture,
                x_account,
                instagram_account,
                discord_account,
                profile_message,
                profile_image,
                user_id
            ))

        else:
            cursor.execute("""
                UPDATE M_USER
                SET
                    USER_NAME = %s,
                    MEMBER_SINCE = %s,
                    EMAIL = %s,
                    GENDER = %s,
                    BIRTHDAY = %s,
                    PREFECTURE = %s,
                    X_ACCOUNT = %s,
                    INSTAGRAM_ACCOUNT = %s,
                    DISCORD_ACCOUNT = %s,
                    PROFILE_MESSAGE = %s
                WHERE USER_ID = %s
            """, (
                user_name,
                member_since,
                email,
                gender,
                birthday,
                prefecture,
                x_account,
                instagram_account,
                discord_account,
                profile_message,
                user_id
            ))

        conn.commit()
        conn.close()

    @staticmethod
    def update_password(user_id, password):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE M_USER
                SET password = %s
                WHERE user_id = %s
                """,
                (
                    password,
                    user_id
                )
            )
            conn.commit()
        finally:
            conn.close()
