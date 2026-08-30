from python.core.database import get_connection


class UserModel:

    @staticmethod
    def update_last_access_at(user_id: str) -> None:
        """最終アクセス日時更新"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE M_USER
                SET
                    LAST_ACCESS_AT = CURRENT_TIMESTAMP
                WHERE
                    USER_ID = %s
            """, (
                user_id,
            ))

            conn.commit()

        finally:
            conn.close()

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
    def exists_email(
            email: str,
            exclude_user_id: str = None
    ) -> bool:
        """メールアドレスが存在するか"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            if exclude_user_id:

                cursor.execute("""
                        SELECT 1
                        FROM M_USER
                        WHERE EMAIL = %s
                        AND USER_ID <> %s
                    """, (
                    email,
                    exclude_user_id
                ))

            else:

                cursor.execute("""
                        SELECT 1
                        FROM M_USER
                        WHERE EMAIL = %s
                    """, (
                    email,
                ))

            result = cursor.fetchone()

            return result is not None

        finally:
            conn.close()

    @staticmethod
    def update_email(
            user_id: str,
            email: str
    ) -> None:
        """メールアドレス更新"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                    UPDATE M_USER
                    SET
                        EMAIL = %s,
                        EMAIL_VERIFIED = FALSE
                    WHERE
                        USER_ID = %s
                """, (
                email,
                user_id
            ))

            conn.commit()

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
    def get_user_by_email(email: str):
        """メールアドレスからユーザー取得"""

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
                    U.EMAIL = %s
                AND U.IS_ACTIVE = TRUE
            """, (email,))

            return cursor.fetchone()

        finally:
            conn.close()

    @staticmethod
    def get_user_by_login_id_and_email(
            login_id: str,
            email: str
    ):
        """ログインIDとメールアドレスからユーザー取得"""

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
                AND U.EMAIL = %s
                AND U.IS_ACTIVE = TRUE
            """, (
                login_id,
                email
            ))

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

    @staticmethod
    def verify_email(
            user_id: str,
            email: str
    ) -> bool:
        """メールアドレスを認証済みにする"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                    UPDATE M_USER
                    SET
                        EMAIL_VERIFIED = TRUE
                    WHERE
                        USER_ID = %s
                    AND EMAIL = %s
                    AND IS_ACTIVE = TRUE
                """, (
                user_id,
                email
            ))

            updated_count = cursor.rowcount

            conn.commit()

            return updated_count > 0

        finally:
            conn.close()

    @staticmethod
    def withdraw_user(user_id: str) -> bool:
        """ユーザーの退会予約"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE M_USER
                SET
                    WITHDRAWAL_AT = CURRENT_TIMESTAMP
                WHERE
                    USER_ID = %s
                    AND ROLE = 'user'
                    AND IS_ACTIVE = TRUE
                    AND WITHDRAWAL_AT IS NULL
            """, (
                user_id,
            ))

            updated_count = cursor.rowcount

            conn.commit()

            return updated_count > 0

        finally:
            conn.close()

    @staticmethod
    def get_all_users_for_admin(
            user_name=None,
            login_id=None,
            role=None,
            is_active=None,
            withdrawal=None
    ):
        """管理者用ユーザー一覧取得"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            sql = """
                SELECT
                    USER_ID,
                    LOGIN_ID,
                    USER_NAME,
                    ROLE,
                    IS_ACTIVE,
                    CREATED_AT,
                    LAST_ACCESS_AT,
                    WITHDRAWAL_AT
                FROM M_USER
                WHERE 1 = 1
            """

            params = []

            # =====================================================
            # 名前
            # =====================================================

            if user_name:
                sql += """
                    AND USER_NAME ILIKE %s
                """
                params.append(f"%{user_name}%")

            # =====================================================
            # ユーザーID
            # =====================================================

            if login_id:
                sql += """
                    AND LOGIN_ID ILIKE %s
                """
                params.append(f"%{login_id}%")

            # =====================================================
            # 権限
            # =====================================================

            if role:
                sql += """
                    AND ROLE = %s
                """
                params.append(role)

            # =====================================================
            # BAN状態
            # =====================================================

            if is_active == "active":
                sql += """
                    AND IS_ACTIVE = TRUE
                """

            elif is_active == "banned":
                sql += """
                    AND IS_ACTIVE = FALSE
                """

            # =====================================================
            # 削除予約
            # =====================================================

            if withdrawal == "reserved":
                sql += """
                    AND WITHDRAWAL_AT IS NOT NULL
                """

            elif withdrawal == "none":
                sql += """
                    AND WITHDRAWAL_AT IS NULL
                """

            # =====================================================
            # 並び順
            # =====================================================

            sql += """
                ORDER BY CREATED_AT DESC
            """

            cursor.execute(sql, params)

            return cursor.fetchall()

        finally:
            conn.close()

    @staticmethod
    def set_active(
            user_id,
            is_active
    ):
        """ユーザーの有効・BAN状態を変更する"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE M_USER
                SET
                    IS_ACTIVE = %s
                WHERE
                    USER_ID = %s
            """, (
                is_active,
                user_id
            ))

            updated = cursor.rowcount > 0

            conn.commit()

            return updated

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def cancel_withdrawal(
            user_id
    ):
        """退会予約を解除する"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE M_USER
                SET
                    WITHDRAWAL_AT = NULL
                WHERE
                    USER_ID = %s
            """, (
                user_id,
            ))

            updated = cursor.rowcount > 0

            conn.commit()

            return updated

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def get_user_for_admin(user_id: str):
        """管理者用ユーザー取得"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    USER_ID,
                    LOGIN_ID,
                    USER_NAME,
                    ROLE,
                    IS_ACTIVE,
                    CREATED_AT,
                    LAST_ACCESS_AT,
                    WITHDRAWAL_AT
                FROM M_USER
                WHERE USER_ID = %s
            """, (
                user_id,
            ))

            return cursor.fetchone()

        finally:
            conn.close()
