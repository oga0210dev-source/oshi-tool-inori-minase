from python.models.image import ImageModel
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
            SELECT *
            FROM M_USER
            WHERE USER_ID = %s
            AND IS_ACTIVE = TRUE
        """, (user_id,))

        user = cursor.fetchone()

        conn.close()

        return user

    @staticmethod
    def update_user(
            user_id,
            user_name,
            member_since,
            email,
            gender,
            birthday,
            profile_image=None
    ):
        if profile_image:

            sql = """
            UPDATE M_USER
            SET
                USER_NAME = %s,
                MEMBER_SINCE = %s,
                EMAIL = %s,
                GENDER = %s,
                BIRTHDAY = %s,
                PROFILE_IMAGE = %s
            WHERE USER_ID = %s
            """

            params = (
                user_name,
                member_since,
                email,
                gender,
                birthday,
                profile_image,
                user_id
            )

        else:

            sql = """
            UPDATE M_USER
            SET
                USER_NAME = %s,
                MEMBER_SINCE = %s,
                EMAIL = %s,
                GENDER = %s,
                BIRTHDAY = %s
            WHERE USER_ID = %s
            """

            params = (
                user_name,
                member_since,
                email,
                gender,
                birthday,
                user_id
            )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(sql, params)

        conn.commit()
        conn.close()
