from python.core.database import get_connection
from python.models.image import ImageModel


def delete_expired_users():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # ================================================
        # 退会予約から30日経過した登録ユーザー
        # ================================================

        cursor.execute("""
            SELECT USER_ID
            FROM M_USER
            WHERE
                ROLE = 'user'
                AND WITHDRAWAL_AT IS NOT NULL
                AND WITHDRAWAL_AT <=
                    CURRENT_TIMESTAMP - INTERVAL '30 days'
        """)

        withdrawal_users = cursor.fetchall()

        for user in withdrawal_users:
            ImageModel.delete_profile_image(
                user["user_id"]
            )

        cursor.execute("""
            DELETE FROM M_USER
            WHERE
                ROLE = 'user'
                AND WITHDRAWAL_AT IS NOT NULL
                AND WITHDRAWAL_AT <=
                    CURRENT_TIMESTAMP - INTERVAL '30 days'
        """)

        withdrawal_deleted_count = cursor.rowcount

        # ================================================
        # 最終アクセスから30日経過したゲスト
        # ================================================

        cursor.execute("""
            SELECT USER_ID
            FROM M_USER
            WHERE
                ROLE = 'guest'
                AND LAST_ACCESS_AT IS NOT NULL
                AND LAST_ACCESS_AT <=
                    CURRENT_TIMESTAMP - INTERVAL '30 days'
        """)

        guest_users = cursor.fetchall()

        for user in guest_users:
            ImageModel.delete_profile_image(
                user["user_id"]
            )

        cursor.execute("""
            DELETE FROM M_USER
            WHERE
                ROLE = 'guest'
                AND LAST_ACCESS_AT IS NOT NULL
                AND LAST_ACCESS_AT <=
                    CURRENT_TIMESTAMP - INTERVAL '30 days'
        """)

        guest_deleted_count = cursor.rowcount

        conn.commit()

        print(
            f"[User Cleanup Batch] 完了 "
            f"退会ユーザー={withdrawal_deleted_count}件 / "
            f"ゲスト={guest_deleted_count}件"
        )

        return {
            "withdrawal_deleted_count": withdrawal_deleted_count,
            "guest_deleted_count": guest_deleted_count
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
