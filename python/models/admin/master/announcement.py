from python.core.database import get_connection


def get_announcement_list(
        keyword=None,
        genre=None,
        status=None
):
    """
    お知らせ一覧取得
    """

    conn = get_connection()

    sql = """
        SELECT
            m_announcement.*

        FROM m_announcement

        WHERE
            m_announcement.is_deleted = FALSE
    """

    params = []

    if keyword:
        sql += """
            AND (
                m_announcement.title ILIKE %s
                OR m_announcement.body ILIKE %s
            )
        """

        params.extend([
            f"%{keyword}%",
            f"%{keyword}%"
        ])

    if genre:
        sql += """
            AND m_announcement.genre = %s
        """

        params.append(genre)

    if status == "active":
        sql += """
            AND m_announcement.is_active = TRUE
        """

    elif status == "inactive":
        sql += """
            AND m_announcement.is_active = FALSE
        """

    sql += """
        ORDER BY
            m_announcement.priority ASC,
            m_announcement.start_at DESC,
            m_announcement.announcement_id DESC
    """

    try:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                params
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_announcement(announcement_id):
    """
    お知らせ取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m_announcement.*

                FROM m_announcement

                WHERE
                    m_announcement.announcement_id = %s
                    AND m_announcement.is_deleted = FALSE
                """,
                (announcement_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def get_public_announcement_list():
    """
    ユーザー向け公開中お知らせ一覧取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m_announcement.*

                FROM m_announcement

                WHERE
                    m_announcement.is_active = TRUE
                    AND m_announcement.is_deleted = FALSE

                    AND m_announcement.start_at <= CURRENT_TIMESTAMP

                    AND (
                        m_announcement.end_at IS NULL
                        OR m_announcement.end_at >= CURRENT_TIMESTAMP
                    )

                ORDER BY
                    m_announcement.genre,
                    m_announcement.priority ASC,
                    m_announcement.start_at DESC,
                    m_announcement.announcement_id DESC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_public_announcement(announcement_id):
    """
    ユーザー向け公開中お知らせ取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m_announcement.*

                FROM m_announcement

                WHERE
                    m_announcement.announcement_id = %s

                    AND m_announcement.is_active = TRUE
                    AND m_announcement.is_deleted = FALSE

                    AND m_announcement.start_at <= CURRENT_TIMESTAMP

                    AND (
                        m_announcement.end_at IS NULL
                        OR m_announcement.end_at >= CURRENT_TIMESTAMP
                    )
                """,
                (announcement_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def create_announcement(announcement):
    """
    お知らせ登録
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_announcement(
                    genre,
                    priority,
                    title,
                    body,
                    start_at,
                    end_at,
                    is_active
                )

                VALUES(
                    %s,%s,%s,%s,%s,%s,%s
                )

                RETURNING announcement_id
                """,
                (
                    announcement["genre"],
                    announcement["priority"],
                    announcement["title"],
                    announcement["body"],
                    announcement["start_at"],
                    announcement["end_at"],
                    announcement["is_active"]
                )
            )

            announcement_id = cur.fetchone()["announcement_id"]

        conn.commit()

        return announcement_id

    finally:
        conn.close()


def update_announcement(
        announcement_id,
        announcement
):
    """
    お知らせ更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_announcement
                SET
                    genre = %s,
                    priority = %s,
                    title = %s,
                    body = %s,
                    start_at = %s,
                    end_at = %s,
                    is_active = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    announcement_id = %s
                """,
                (
                    announcement["genre"],
                    announcement["priority"],
                    announcement["title"],
                    announcement["body"],
                    announcement["start_at"],
                    announcement["end_at"],
                    announcement["is_active"],
                    announcement_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def update_announcement_status(
        announcement_id,
        is_active
):
    """
    お知らせ公開状態更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_announcement
                SET
                    is_active = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    announcement_id = %s
                """,
                (
                    is_active,
                    announcement_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_announcement(announcement_id):
    """
    お知らせ論理削除
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_announcement
                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    announcement_id = %s
                """,
                (announcement_id,)
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
