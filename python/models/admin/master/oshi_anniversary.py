from python.core.database import get_connection


def get_anniversary_list(
        keyword="",
        sort="date_asc"
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
                        anniversary_name ILIKE %s
                        OR description ILIKE %s
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
                "date_asc": """
                    anniversary_date ASC,
                    anniversary_id ASC
                """,
                "date_desc": """
                    anniversary_date DESC,
                    anniversary_id DESC
                """,
                "name": """
                    anniversary_name ASC,
                    anniversary_id ASC
                """,
                "created": """
                    created_at DESC,
                    anniversary_id DESC
                """,
                "updated": """
                    updated_at DESC,
                    anniversary_id DESC
                """
            }

            order_sql = sort_map.get(
                sort,
                sort_map["date_asc"]
            )

            cur.execute(
                f"""
                SELECT
                    anniversary_id,
                    anniversary_name,
                    anniversary_date,
                    description,
                    display_order,
                    public_flag,
                    created_at,
                    updated_at
                FROM m_oshi_anniversary
                WHERE
                    {where_sql}
                ORDER BY
                    {order_sql}
                """,
                tuple(params)
            )

            anniversaries = cur.fetchall()

            for anniversary in anniversaries:

                if anniversary["description"]:
                    anniversary["description"] = (
                        anniversary["description"].strip()
                    )

            return anniversaries

    finally:
        conn.close()


def get_anniversary(
        anniversary_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    anniversary_id,
                    anniversary_name,
                    anniversary_date,
                    description,
                    display_order,
                    public_flag
                FROM m_oshi_anniversary
                WHERE
                    anniversary_id = %s
                    AND is_deleted = FALSE
                """,
                (anniversary_id,)
            )

            anniversary = cur.fetchone()

            if anniversary and anniversary["description"]:
                anniversary["description"] = (
                    anniversary["description"].strip()
                )

            return anniversary

    finally:
        conn.close()


def create_anniversary(
        anniversary_name,
        anniversary_date,
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
                FROM m_oshi_anniversary
                WHERE
                    is_deleted = FALSE
                """
            )

            result = cur.fetchone()

            display_order = result["next_display_order"]

            cur.execute(
                """
                INSERT INTO m_oshi_anniversary (
                    anniversary_name,
                    anniversary_date,
                    description,
                    display_order,
                    public_flag
                )
                VALUES (
                    %s, %s, %s, %s, %s
                )
                """,
                (
                    anniversary_name,
                    anniversary_date,
                    description,
                    display_order,
                    public_flag
                )
            )

        conn.commit()

    finally:
        conn.close()


def update_anniversary(
        anniversary_id,
        anniversary_name,
        anniversary_date,
        description,
        public_flag
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE m_oshi_anniversary
                SET
                    anniversary_name = %s,
                    anniversary_date = %s,
                    description = %s,
                    public_flag = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    anniversary_id = %s
                    AND is_deleted = FALSE
                """,
                (
                    anniversary_name,
                    anniversary_date,
                    description,
                    public_flag,
                    anniversary_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_anniversary(
        anniversary_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE m_oshi_anniversary
                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    anniversary_id = %s
                """,
                (anniversary_id,)
            )

        conn.commit()

    finally:
        conn.close()
