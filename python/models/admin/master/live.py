from python.core.database import get_connection


def get_live_list(keyword=None, sort="tour"):
    conn = get_connection()

    if sort == "date_desc":
        order_by = """
            live_date DESC,
            tour_order ASC
        """

    elif sort == "date_asc":
        order_by = """
            live_date ASC,
            tour_order ASC
        """

    elif sort == "name":
        order_by = """
            live_name ASC
        """

    elif sort == "updated":
        order_by = """
            m_live.updated_at DESC
        """

    else:
        # デフォルト
        # ツアー順
        order_by = """
            live_date ASC,
            tour_order ASC
        """

    sql = """
        SELECT
            m_live.live_id,
            m_live.live_name,
            m_live.tour_name,
            m_live.tour_order,
            m_live.live_date,
            m_live.venue_name,
            m_live.prefecture_code,
            m_prefecture.prefecture_name,
            m_live.blu_ray_url,
            m_live.official_url,
            m_live.public_flag,
            m_live.created_at,
            m_live.updated_at

        FROM m_live

        LEFT JOIN m_prefecture
        ON m_live.prefecture_code = m_prefecture.prefecture_code

        WHERE
            m_live.is_deleted = FALSE
    """

    params = []

    if keyword:
        sql += """
            AND (
                m_live.live_name ILIKE %s
                OR m_live.tour_name ILIKE %s
                OR m_live.venue_name ILIKE %s
            )
        """

        params.extend([
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ])

    sql += f"""
        ORDER BY
        {order_by}
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


def get_live(live_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m_live.*,
                    m_prefecture.prefecture_name

                FROM m_live

                LEFT JOIN m_prefecture
                ON m_live.prefecture_code = m_prefecture.prefecture_code

                WHERE
                    live_id = %s
                    AND is_deleted = FALSE
                """,
                (live_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()


def create_live(live):
    """
    ライブ登録
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_live(
                    live_name,
                    tour_name,
                    tour_order,
                    live_date,
                    venue_name,
                    prefecture_code,
                    blu_ray_url,
                    official_url,
                    public_flag
                )

                VALUES(
                    %s,%s,%s,%s,%s,
                    %s,%s,%s,%s
                )

                RETURNING live_id
                """,
                (
                    live["live_name"],
                    live["tour_name"],
                    live["tour_order"],
                    live["live_date"],
                    live["venue_name"],
                    live["prefecture_code"],
                    live["blu_ray_url"],
                    live["official_url"],
                    live["public_flag"]
                )
            )
            live_id = cur.fetchone()["live_id"]
        conn.commit()
        return live_id
    finally:
        conn.close()


def update_live(live_id, live):
    """
    ライブ更新
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_live
                SET
                    live_name = %s,
                    tour_name = %s,
                    tour_order = %s,
                    live_date = %s,
                    venue_name = %s,
                    prefecture_code = %s,
                    blu_ray_url = %s,
                    official_url = %s,
                    public_flag = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    live_id = %s
                """,
                (
                    live["live_name"],
                    live["tour_name"],
                    live["tour_order"],
                    live["live_date"],
                    live["venue_name"],
                    live["prefecture_code"],
                    live["blu_ray_url"],
                    live["official_url"],
                    live["public_flag"],
                    live_id
                )
            )
        conn.commit()
    finally:
        conn.close()


def delete_live(live_id):
    """
    ライブ論理削除
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_live
                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    live_id = %s
                """,
                (live_id,)
            )
        conn.commit()
    finally:
        conn.close()


def get_tour_list():
    """
    ツアー一覧取得（入力補完用）
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    tour_name,
                    MAX(live_date) AS latest_date
                FROM m_live
                WHERE
                    is_deleted = FALSE
                    AND tour_name IS NOT NULL
                    AND tour_name <> ''
                GROUP BY
                    tour_name
                ORDER BY
                    latest_date DESC
                """
            )
            return cur.fetchall()
    finally:
        conn.close()
