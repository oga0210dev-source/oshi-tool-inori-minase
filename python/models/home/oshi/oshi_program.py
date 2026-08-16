from python.core.database import get_connection


def get_program_list(
        keyword=None,
        program_type=None,
        sort="display"
):
    """
    公開中の番組一覧取得
    """

    conn = get_connection()

    if sort == "name":
        order_by = """
            program_name ASC,
            program_id ASC
        """

    elif sort == "start_date_desc":
        order_by = """
            start_date DESC NULLS LAST,
            display_order ASC,
            program_id ASC
        """

    elif sort == "start_date_asc":
        order_by = """
            start_date ASC NULLS LAST,
            display_order ASC,
            program_id ASC
        """

    else:
        order_by = """
            display_order ASC,
            start_date ASC NULLS LAST,
            program_id ASC
        """

    sql = """
        SELECT
            program_id,
            program_name,
            program_type,
            start_date,
            end_date,
            official_url,
            description

        FROM m_oshi_program

        WHERE
            public_flag = TRUE
            AND is_deleted = FALSE
    """

    params = []

    if keyword:
        sql += """
            AND (
                program_name ILIKE %s
                OR description ILIKE %s
            )
        """

        keyword_param = f"%{keyword}%"

        params.extend([
            keyword_param,
            keyword_param
        ])

    if program_type:
        sql += """
            AND program_type = %s
        """

        params.append(program_type)

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
