from python.core.database import get_connection


def get_oshi_official_link_list():
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
                    description
                FROM m_oshi_official_link
                WHERE
                    public_flag = TRUE
                    AND is_deleted = FALSE
                ORDER BY
                    display_order ASC,
                    link_id ASC
                """
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
