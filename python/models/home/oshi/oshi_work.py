from python.core.database import get_connection


BROADCAST_SEASON_NAMES = {
    "SPRING": "春",
    "SUMMER": "夏",
    "AUTUMN": "秋",
    "WINTER": "冬"
}


def get_oshi_work_list(
        keyword="",
        sort="release_asc"
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            conditions = [
                "is_deleted = FALSE",
                "public_flag = TRUE"
            ]

            params = []

            if keyword:
                conditions.append(
                    """
                    (
                        work_name ILIKE %s
                        OR character_name ILIKE %s
                        OR description ILIKE %s
                    )
                    """
                )

                search_keyword = f"%{keyword}%"

                params.extend([
                    search_keyword,
                    search_keyword,
                    search_keyword
                ])

            where_sql = " AND ".join(conditions)

            sort_map = {
                "release_asc": """
                    CASE
                        WHEN work_type = 'ANIME'
                        THEN broadcast_year
                    END ASC NULLS LAST,
                    CASE
                        WHEN work_type = 'ANIME'
                        THEN CASE broadcast_season
                            WHEN 'SPRING' THEN 1
                            WHEN 'SUMMER' THEN 2
                            WHEN 'AUTUMN' THEN 3
                            WHEN 'WINTER' THEN 4
                        END
                    END ASC NULLS LAST,
                    release_date ASC NULLS LAST,
                    work_id ASC
                """,

                "release_desc": """
                    CASE
                        WHEN work_type = 'ANIME'
                        THEN broadcast_year
                    END DESC NULLS LAST,
                    CASE
                        WHEN work_type = 'ANIME'
                        THEN CASE broadcast_season
                            WHEN 'SPRING' THEN 1
                            WHEN 'SUMMER' THEN 2
                            WHEN 'AUTUMN' THEN 3
                            WHEN 'WINTER' THEN 4
                        END
                    END DESC NULLS LAST,
                    release_date DESC NULLS LAST,
                    work_id DESC
                """,

                "name": """
                    work_name ASC,
                    work_id ASC
                """,

                "type": """
                    work_type ASC,
                    CASE
                        WHEN work_type = 'ANIME'
                        THEN broadcast_year
                    END ASC NULLS LAST,
                    release_date ASC NULLS LAST,
                    work_id ASC
                """
            }

            order_sql = sort_map.get(
                sort,
                sort_map["release_asc"]
            )

            cur.execute(
                f"""
                SELECT
                    work_id,
                    work_name,
                    work_type,
                    character_name,
                    release_date,
                    broadcast_year,
                    broadcast_season,
                    official_url,
                    description
                FROM m_oshi_work
                WHERE
                    {where_sql}
                ORDER BY
                    {order_sql}
                """,
                tuple(params)
            )

            works = cur.fetchall()

            for work in works:

                if work["character_name"]:
                    work["character_name"] = (
                        work["character_name"].strip()
                    )

                if work["description"]:
                    work["description"] = (
                        work["description"].strip()
                    )

                work["broadcast_season_name"] = (
                    BROADCAST_SEASON_NAMES.get(
                        work["broadcast_season"]
                    )
                )

            return works

    finally:
        conn.close()
