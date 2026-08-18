from python.core.database import get_connection


def get_invitation_code_list():
    """
    招待コード一覧取得
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
                    expires_at,
                    created_at,
                    updated_at
                FROM m_invitation_code
                ORDER BY
                    created_at DESC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_invitation_code(invitation_code):
    """
    招待コード取得
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
                    expires_at,
                    created_at,
                    updated_at
                FROM m_invitation_code
                WHERE invitation_code = %s
                """,
                (invitation_code,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def create_invitation_code(invitation_code, max_usage, expires_at):
    """
    招待コード登録
    """
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_invitation_code(
                    invitation_code,
                    max_usage,
                    expires_at
                )
                VALUES(
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    invitation_code,
                    max_usage,
                    expires_at
                )
            )

        conn.commit()

    finally:
        conn.close()


def update_invitation_code(
        invitation_code,
        is_active,
        max_usage,
        expires_at
):
    """
    招待コード更新
    """
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_invitation_code
                SET
                    is_active = %s,
                    max_usage = %s,
                    expires_at = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    invitation_code = %s
                """,
                (
                    is_active,
                    max_usage,
                    expires_at,
                    invitation_code
                )
            )

        conn.commit()

    finally:
        conn.close()


def toggle_invitation_code(invitation_code):
    """
    招待コードの有効 / 無効を切り替え
    """
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_invitation_code
                SET
                    is_active = NOT is_active,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    invitation_code = %s
                """,
                (invitation_code,)
            )

        conn.commit()

    finally:
        conn.close()
