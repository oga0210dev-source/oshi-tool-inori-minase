from python.core.database import get_connection


def get_active_maintenance():
    """
    現在有効なメンテナンス一覧取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    maintenance_id,
                    announcement_id,
                    maintenance_type,
                    target_key,
                    title,
                    message,
                    start_at,
                    end_at,
                    is_emergency,
                    is_active,
                    created_at,
                    updated_at
                FROM m_maintenance
                WHERE
                    is_active = TRUE
                    AND (
                        start_at IS NULL
                        OR start_at <= CURRENT_TIMESTAMP
                    )
                    AND (
                        end_at IS NULL
                        OR end_at >= CURRENT_TIMESTAMP
                    )
                ORDER BY
                    maintenance_id DESC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_maintenance_by_id(maintenance_id):
    """
    メンテナンス取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    maintenance_id,
                    announcement_id,
                    maintenance_type,
                    target_key,
                    title,
                    message,
                    start_at,
                    end_at,
                    is_emergency,
                    is_active,
                    created_at,
                    updated_at
                FROM m_maintenance
                WHERE
                    maintenance_id = %s
                """,
                (maintenance_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def is_maintenance(target_key=None):
    """
    指定した機能が現在メンテナンス中か判定

    ALL:
        サービス全体がメンテナンス中

    PARTIAL:
        指定したtarget_keyがメンテナンス中
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    maintenance_type
                FROM m_maintenance
                WHERE
                    is_active = TRUE
                    AND (
                        start_at IS NULL
                        OR start_at <= CURRENT_TIMESTAMP
                    )
                    AND (
                        end_at IS NULL
                        OR end_at >= CURRENT_TIMESTAMP
                    )
                    AND (
                        maintenance_type = 'ALL'
                        OR (
                            maintenance_type = 'PARTIAL'
                            AND target_key = %s
                        )
                    )
                LIMIT 1
                """,
                (target_key,)
            )

            return cur.fetchone() is not None

    finally:
        conn.close()


def can_start_normal_maintenance(maintenance_id):
    """
    通常メンテナンスの開始可否判定

    紐付けられたメンテナンス告知が公開されてから
    24時間以上経過している場合のみTRUE。

    緊急メンテナンスの場合は24時間ルール対象外。
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m.is_emergency,
                    a.start_at
                FROM m_maintenance m
                LEFT JOIN m_announcement a
                    ON m.announcement_id = a.announcement_id
                    AND a.genre = 'MAINTENANCE'
                    AND a.is_active = TRUE
                    AND a.is_deleted = FALSE
                    AND a.start_at <= CURRENT_TIMESTAMP
                WHERE
                    m.maintenance_id = %s
                """,
                (maintenance_id,)
            )

            maintenance = cur.fetchone()

            if not maintenance:
                return False

            # 緊急メンテナンスは24時間ルール対象外
            if maintenance["is_emergency"]:
                return True

            # 通常メンテナンスは有効な告知が必須
            if maintenance["start_at"] is None:
                return False

            # 告知公開から24時間以上経過しているか
            cur.execute(
                """
                SELECT
                    %s <= CURRENT_TIMESTAMP - INTERVAL '24 hours' AS can_start
                """,
                (maintenance["start_at"],)
            )

            return cur.fetchone()["can_start"]

    finally:
        conn.close()


def get_maintenance_list():
    """
    メンテナンス一覧取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    maintenance_id,
                    announcement_id,
                    maintenance_type,
                    target_key,
                    title,
                    message,
                    start_at,
                    end_at,
                    is_emergency,
                    is_active,
                    created_at,
                    updated_at
                FROM m_maintenance
                ORDER BY
                    maintenance_id DESC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()


def create_maintenance(maintenance):
    """
    メンテナンス登録
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_maintenance (
                    announcement_id,
                    maintenance_type,
                    target_key,
                    title,
                    message,
                    start_at,
                    end_at,
                    is_emergency,
                    is_active
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                RETURNING maintenance_id
                """,
                (
                    maintenance["announcement_id"],
                    maintenance["maintenance_type"],
                    maintenance["target_key"],
                    maintenance["title"],
                    maintenance["message"],
                    maintenance["start_at"],
                    maintenance["end_at"],
                    maintenance["is_emergency"],
                    maintenance["is_active"]
                )
            )

            maintenance_id = cur.fetchone()["maintenance_id"]

        conn.commit()

        return maintenance_id

    finally:
        conn.close()


def update_maintenance(maintenance_id, maintenance):
    """
    メンテナンス更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_maintenance
                SET
                    announcement_id = %s,
                    maintenance_type = %s,
                    target_key = %s,
                    title = %s,
                    message = %s,
                    start_at = %s,
                    end_at = %s,
                    is_emergency = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    maintenance_id = %s
                """,
                (
                    maintenance["announcement_id"],
                    maintenance["maintenance_type"],
                    maintenance["target_key"],
                    maintenance["title"],
                    maintenance["message"],
                    maintenance["start_at"],
                    maintenance["end_at"],
                    maintenance["is_emergency"],
                    maintenance_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def update_maintenance_status(maintenance_id, is_active):
    """
    メンテナンス状態更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_maintenance
                SET
                    is_active = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    maintenance_id = %s
                """,
                (
                    is_active,
                    maintenance_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def get_maintenance_announcement_list():
    """
    メンテナンス告知一覧取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    announcement_id,
                    title,
                    body,
                    start_at,
                    end_at,
                    is_active,
                    is_deleted
                FROM m_announcement
                WHERE
                    genre = 'MAINTENANCE'
                    AND is_deleted = FALSE
                ORDER BY
                    start_at DESC,
                    announcement_id DESC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()
