from python.core.database import get_connection


def get_work_list(
        keyword="",
        sort="created"
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            conditions = [
                "is_deleted = FALSE"
            ]

            params = []

            if keyword:
                conditions.append(
                    """
                    (
                        work_name ILIKE %s
                        OR character_name ILIKE %s
                    )
                    """
                )

                search_keyword = f"%{keyword}%"

                params.extend([
                    search_keyword,
                    search_keyword
                ])

            where_sql = " AND ".join(conditions)

            sort_map = {
                "created": """
                    created_at DESC,
                    work_id DESC
                """,
                "release_asc": """
                    CASE
                        WHEN work_type = 'ANIME'
                            THEN broadcast_year
                        ELSE
                            EXTRACT(YEAR FROM release_date)
                    END ASC NULLS LAST,

                    CASE
                        WHEN work_type = 'ANIME'
                            THEN CASE broadcast_season
                                WHEN 'SPRING' THEN 1
                                WHEN 'SUMMER' THEN 2
                                WHEN 'AUTUMN' THEN 3
                                WHEN 'WINTER' THEN 4
                                ELSE 5
                            END
                        ELSE
                            EXTRACT(MONTH FROM release_date)
                    END ASC NULLS LAST,

                    release_date ASC NULLS LAST,
                    work_id ASC
                """,
                "release_desc": """
                    CASE
                        WHEN work_type = 'ANIME'
                            THEN broadcast_year
                        ELSE
                            EXTRACT(YEAR FROM release_date)
                    END DESC NULLS LAST,

                    CASE
                        WHEN work_type = 'ANIME'
                            THEN CASE broadcast_season
                                WHEN 'SPRING' THEN 1
                                WHEN 'SUMMER' THEN 2
                                WHEN 'AUTUMN' THEN 3
                                WHEN 'WINTER' THEN 4
                                ELSE 5
                            END
                        ELSE
                            EXTRACT(MONTH FROM release_date)
                    END DESC NULLS LAST,

                    release_date DESC NULLS LAST,
                    work_id DESC
                """,
                "name": """
                    work_name ASC,
                    work_id ASC
                """,
                "updated": """
                    updated_at DESC,
                    work_id DESC
                """
            }

            order_sql = sort_map.get(
                sort,
                sort_map["created"]
            )

            cur.execute(
                f"""
                SELECT
                    work_id,
                    work_name,
                    work_type,

                    CASE work_type
                        WHEN 'ANIME' THEN 'アニメ'
                        WHEN 'MOVIE' THEN '映画'
                        WHEN 'GAME' THEN 'ゲーム'
                        WHEN 'DRAMA' THEN 'ドラマCD'
                        WHEN 'OTHER' THEN 'その他'
                    END AS work_type_name,

                    character_name,

                    release_date,
                    broadcast_year,
                    broadcast_season,

                    official_url,
                    description,
                    display_order,
                    public_flag

                FROM m_oshi_work

                WHERE
                    {where_sql}

                ORDER BY
                    {order_sql}
                """,
                tuple(params)
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_work(work_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    work_id,
                    work_name,
                    work_type,
                    character_name,
                    release_date,
                    broadcast_year,
                    broadcast_season,
                    official_url,
                    description,
                    display_order,
                    public_flag

                FROM m_oshi_work

                WHERE
                    work_id = %s
                    AND is_deleted = FALSE
                """,
                (work_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def create_work(
        work_name,
        work_type,
        character_name,
        release_date,
        broadcast_year,
        broadcast_season,
        official_url,
        description,
        public_flag
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COALESCE(MAX(display_order), 0) + 1 AS next_display_order
                FROM m_oshi_work
                WHERE
                    is_deleted = FALSE
                """
            )

            display_order = cur.fetchone()["next_display_order"]

            cur.execute(
                """
                INSERT INTO m_oshi_work (
                    work_name,
                    work_type,
                    character_name,
                    release_date,
                    broadcast_year,
                    broadcast_season,
                    official_url,
                    description,
                    display_order,
                    public_flag
                )

                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                """,
                (
                    work_name,
                    work_type,
                    character_name,
                    release_date,
                    broadcast_year,
                    broadcast_season,
                    official_url,
                    description,
                    display_order,
                    public_flag
                )
            )

        conn.commit()

    finally:
        conn.close()


def update_work(
        work_id,
        work_name,
        work_type,
        character_name,
        release_date,
        broadcast_year,
        broadcast_season,
        official_url,
        description,
        public_flag
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_oshi_work

                SET
                    work_name = %s,
                    work_type = %s,
                    character_name = %s,
                    release_date = %s,
                    broadcast_year = %s,
                    broadcast_season = %s,
                    official_url = %s,
                    description = %s,
                    public_flag = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    work_id = %s
                    AND is_deleted = FALSE
                """,
                (
                    work_name,
                    work_type,
                    character_name,
                    release_date,
                    broadcast_year,
                    broadcast_season,
                    official_url,
                    description,
                    public_flag,
                    work_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_work(work_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_oshi_work

                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    work_id = %s
                    AND is_deleted = FALSE
                """,
                (work_id,)
            )

        conn.commit()

    finally:
        conn.close()
