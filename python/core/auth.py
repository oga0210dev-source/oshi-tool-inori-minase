from python.core.database import get_connection


def is_login(request):
    return bool(request.session.get("user_id"))


def is_admin(request):
    return request.session.get("role") == "admin"


def get_registration_mode():
    """
    ユーザ登録モードを取得

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


def get_invitation_code(invitation_code):
    """
    招待コードを取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    invitation_code,
                    is_active,
                    max_usage,
                    usage_count,
                    expires_at
                FROM m_invitation_code
                WHERE invitation_code = %s
                """,
                (invitation_code,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def is_valid_invitation_code(invitation_code):
    """
    招待コードが現在使用可能か確認
    """

    code = get_invitation_code(invitation_code)

    if not code:
        return False

    if not code["is_active"]:
        return False

    if (
        code["max_usage"] is not None
        and code["usage_count"] >= code["max_usage"]
    ):
        return False

    if code["expires_at"] is not None:
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT CURRENT_TIMESTAMP < %s AS is_valid
                    """,
                    (code["expires_at"],)
                )

                result = cur.fetchone()

                if not result["is_valid"]:
                    return False

        finally:
            conn.close()

    return True


def use_invitation_code(invitation_code):
    """
    招待コードの使用回数を1増やす
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_invitation_code
                SET
                    usage_count = usage_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE invitation_code = %s
                  AND is_active = TRUE
                  AND (
                      max_usage IS NULL
                      OR usage_count < max_usage
                  )
                  AND (
                      expires_at IS NULL
                      OR expires_at > CURRENT_TIMESTAMP
                  )
                """,
                (invitation_code,)
            )

            updated_count = cur.rowcount

        conn.commit()

        return updated_count > 0

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
