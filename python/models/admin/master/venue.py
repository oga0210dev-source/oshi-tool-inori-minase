from python.core.database import get_connection


def get_venue_list(keyword=None, sort="name"):
    conn = get_connection()

    if sort == "updated":
        order_by = "v.updated_at DESC"
    elif sort == "prefecture":
        order_by = """
            v.prefecture_code ASC,
            v.venue_name ASC
        """
    else:
        order_by = "v.venue_name ASC"

    sql = f"""
        SELECT
            v.venue_id,
            v.venue_name,
            v.address,
            v.prefecture_code,
            p.prefecture_name,
            v.latitude,
            v.longitude,
            v.public_flag,
            v.created_at,
            v.updated_at

        FROM m_venue v

        LEFT JOIN m_prefecture p
            ON v.prefecture_code = p.prefecture_code

        WHERE
            v.is_deleted = FALSE
    """

    params = []

    if keyword:
        sql += """
            AND (
                v.venue_name ILIKE %s
                OR v.address ILIKE %s
            )
        """

        params.extend([
            f"%{keyword}%",
            f"%{keyword}%"
        ])

    sql += f"""
        ORDER BY
            {order_by}
    """

    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def get_venue(venue_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    v.*,
                    p.prefecture_name
                FROM m_venue v

                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code

                WHERE
                    v.venue_id = %s
                    AND v.is_deleted = FALSE
                """,
                (venue_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def create_venue(venue):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_venue (
                    venue_name,
                    address,
                    prefecture_code,
                    latitude,
                    longitude,
                    public_flag
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                RETURNING venue_id
                """,
                (
                    venue["venue_name"],
                    venue["address"],
                    venue["prefecture_code"],
                    venue["latitude"],
                    venue["longitude"],
                    venue["public_flag"]
                )
            )

            venue_id = cur.fetchone()["venue_id"]

        conn.commit()

        return venue_id

    finally:
        conn.close()


def update_venue(venue_id, venue):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_venue
                SET
                    venue_name = %s,
                    address = %s,
                    prefecture_code = %s,
                    latitude = %s,
                    longitude = %s,
                    public_flag = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    venue_id = %s
                """,
                (
                    venue["venue_name"],
                    venue["address"],
                    venue["prefecture_code"],
                    venue["latitude"],
                    venue["longitude"],
                    venue["public_flag"],
                    venue_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_venue(venue_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_venue
                SET
                    is_deleted = TRUE,
                    public_flag = FALSE,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    venue_id = %s
                """,
                (venue_id,)
            )

        conn.commit()

    finally:
        conn.close()
