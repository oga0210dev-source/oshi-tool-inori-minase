from python.core.database import get_connection


class UserModel:

    @staticmethod
    def exists_user_id(user_id: str) -> bool:
        """ユーザーIDが存在するか"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 1
                FROM M_USER
                WHERE USER_ID = %s
            """, (user_id,))

            result = cursor.fetchone()

            return result is not None

        finally:
            conn.close()

    @staticmethod
    def exists_login_id(login_id: str) -> bool:
        """ログインIDが存在するか"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 1
                FROM M_USER
                WHERE LOGIN_ID = %s
            """, (login_id,))

            result = cursor.fetchone()

            return result is not None

        finally:
            conn.close()

    @staticmethod
    def create_user(
            user_id: str,
            user_name: str,
            password: str
    ) -> None:
        """ユーザー登録"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO M_USER
                (
                    USER_ID,
                    USER_NAME,
                    PASSWORD,
                    ROLE,
                    LOGIN_ID
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    'user',
                    %s
                )
            """, (
                user_id,
                user_name,
                password,
                user_id
            ))

            conn.commit()

        finally:
            conn.close()

    @staticmethod
    def get_user(user_id: str):
        """ユーザー取得"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    U.*,
                    P.PREFECTURE_NAME
                FROM M_USER U
                LEFT JOIN M_PREFECTURE P
                    ON U.PREFECTURE = P.PREFECTURE_CODE
                WHERE
                    U.USER_ID = %s
                AND U.IS_ACTIVE = TRUE
            """, (user_id,))

            return cursor.fetchone()

        finally:
            conn.close()

    @staticmethod
    def get_user_by_login_id(login_id: str):
        """ログインIDからユーザー取得"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    U.*,
                    P.PREFECTURE_NAME
                FROM M_USER U
                LEFT JOIN M_PREFECTURE P
                    ON U.PREFECTURE = P.PREFECTURE_CODE
                WHERE
                    U.LOGIN_ID = %s
                AND U.IS_ACTIVE = TRUE
            """, (login_id,))

            return cursor.fetchone()

        finally:
            conn.close()

    @staticmethod
    def get_user_by_guest_uuid(guest_uuid: str):
        """ゲストUUIDからゲストユーザー取得"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    U.*,
                    P.PREFECTURE_NAME
                FROM M_USER U
                LEFT JOIN M_PREFECTURE P
                    ON U.PREFECTURE = P.PREFECTURE_CODE
                WHERE
                    U.GUEST_UUID = %s
                AND U.ROLE = 'guest'
                AND U.IS_ACTIVE = TRUE
            """, (guest_uuid,))

            return cursor.fetchone()

        finally:
            conn.close()

    @staticmethod
    def create_guest_user(
            user_id: str,
            guest_uuid: str
    ) -> None:
        """ゲストユーザー作成"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO M_USER
                (
                    USER_ID,
                    USER_NAME,
                    PASSWORD,
                    ROLE,
                    LOGIN_ID,
                    GUEST_UUID,
                    EMAIL_VERIFIED
                )
                VALUES
                (
                    %s,
                    %s,
                    NULL,
                    'guest',
                    NULL,
                    %s,
                    FALSE
                )
            """, (
                user_id,
                "ゲストユーザー",
                guest_uuid
            ))

            conn.commit()

        finally:
            conn.close()

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

        try:
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

        finally:
            conn.close()

    @staticmethod
    def update_password(user_id, password):
        """パスワード変更"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE M_USER
                SET PASSWORD = %s
                WHERE USER_ID = %s
            """, (
                password,
                user_id
            ))

            conn.commit()

        finally:
            conn.close()

    @staticmethod
    def convert_guest_to_user(
            user_id: str,
            login_id: str,
            user_name: str,
            password: str
    ) -> bool:
        """ゲストユーザーを本登録ユーザーへ変更"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE M_USER
                SET
                    USER_NAME = %s,
                    PASSWORD = %s,
                    ROLE = 'user',
                    LOGIN_ID = %s
                WHERE
                    USER_ID = %s
                AND ROLE = 'guest'
                AND IS_ACTIVE = TRUE
            """, (
                user_name,
                password,
                login_id,
                user_id
            ))

            updated_count = cursor.rowcount

            conn.commit()

            return updated_count > 0

        finally:
            conn.close()
