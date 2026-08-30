from python.core.database import get_connection


def is_login(request):
    return bool(request.session.get("user_id"))


def is_admin(request):
    return request.session.get("role") == "admin"


def update_last_access(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE M_USER
            SET
                LAST_ACCESS_AT = CURRENT_TIMESTAMP,
                WITHDRAWAL_AT = NULL
            WHERE
                USER_ID = %s
        """, (
            user_id,
        ))

        conn.commit()

    finally:
        conn.close()
