from python.core.database import get_connection


def get_official_link_list(
        keyword="",
        sort="display"
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
                        link_name ILIKE %s
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
                "display": """
                    display_order ASC,
                    link_id ASC
                """,
                "name": """
                    link_name ASC,
                    link_id ASC
                """,
                "created": """
                    created_at DESC,
                    link_id DESC
                """,
                "updated": """
                    updated_at DESC,
                    link_id DESC
                """
            }

            order_sql = sort_map.get(
                sort,
                sort_map["display"]
            )

            cur.execute(
                f"""
                SELECT
                    link_id,
                    link_name,
                    url,
                    icon,
                    description,
                    display_order,
                    public_flag,
                    created_at,
                    updated_at
                FROM m_oshi_official_link
                WHERE
                    {where_sql}
                ORDER BY
                    {order_sql}
                """,
                tuple(params)
            )

            links = cur.fetchall()

            for link in links:

                if link["link_name"]:
                    link["link_name"] = (
                        link["link_name"].strip()
                    )

                if link["icon"]:
                    link["icon"] = (
                        link["icon"].strip()
                    )

                if link["description"]:
                    link["description"] = (
                        link["description"].strip()
                    )

            return links

    finally:
        conn.close()


def get_official_link(
        link_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    link_id,
                    link_name,
                    url,
                    icon,
                    description,
                    display_order,
                    public_flag
                FROM m_oshi_official_link
                WHERE
                    link_id = %s
                    AND is_deleted = FALSE
                """,
                (link_id,)
            )

            link = cur.fetchone()

            if link:

                if link["link_name"]:
                    link["link_name"] = (
                        link["link_name"].strip()
                    )

                if link["icon"]:
                    link["icon"] = (
                        link["icon"].strip()
                    )

                if link["description"]:
                    link["description"] = (
                        link["description"].strip()
                    )

            return link

    finally:
        conn.close()


def create_official_link(
        link_name,
        url,
        icon,
        description,
        public_flag
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    COALESCE(
                        MAX(display_order),
                        0
                    ) + 1 AS next_display_order
                FROM m_oshi_official_link
                WHERE
                    is_deleted = FALSE
                """
            )

            result = cur.fetchone()

            display_order = result[
                "next_display_order"
            ]

            cur.execute(
                """
                INSERT INTO m_oshi_official_link (
                    link_name,
                    url,
                    icon,
                    description,
                    display_order,
                    public_flag
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    link_name,
                    url,
                    icon,
                    description,
                    display_order,
                    public_flag
                )
            )

        conn.commit()

    finally:
        conn.close()


def update_official_link(
        link_id,
        link_name,
        url,
        icon,
        description,
        public_flag
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE m_oshi_official_link
                SET
                    link_name = %s,
                    url = %s,
                    icon = %s,
                    description = %s,
                    public_flag = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    link_id = %s
                    AND is_deleted = FALSE
                """,
                (
                    link_name,
                    url,
                    icon,
                    description,
                    public_flag,
                    link_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_official_link(
        link_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE m_oshi_official_link
                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    link_id = %s
                """,
                (link_id,)
            )

        conn.commit()

    finally:
        conn.close()
