from python.core.database import get_connection


def get_program_list(keyword=None, program_type=None, sort="display"):
    conn = get_connection()

    if sort == "name":
        order_by = """
            program_name ASC
        """

    elif sort == "start_date_desc":
        order_by = """
            start_date DESC NULLS LAST,
            display_order ASC
        """

    elif sort == "start_date_asc":
        order_by = """
            start_date ASC NULLS LAST,
            display_order ASC
        """

    elif sort == "updated":
        order_by = """
            updated_at DESC
        """

    else:
        # デフォルト
        # 表示順 → 開始日
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
            description,
            display_order,
            public_flag,
            created_at,
            updated_at

        FROM m_oshi_program

        WHERE
            is_deleted = FALSE
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


def get_program(program_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    program_id,
                    program_name,
                    program_type,
                    start_date,
                    end_date,
                    official_url,
                    description,
                    display_order,
                    public_flag,
                    created_at,
                    updated_at

                FROM m_oshi_program

                WHERE
                    program_id = %s
                    AND is_deleted = FALSE
                """,
                (program_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def create_program(program):
    """
    番組登録
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_oshi_program(
                    program_name,
                    program_type,
                    start_date,
                    end_date,
                    official_url,
                    description,
                    display_order,
                    public_flag
                )

                VALUES(
                    %s,%s,%s,%s,%s,%s,
                    COALESCE(
                        (
                            SELECT MAX(display_order)
                            FROM m_oshi_program
                            WHERE is_deleted = FALSE
                        ),
                        0
                    ) + 1,
                    %s
                )

                RETURNING program_id
                """,
                (
                    program["program_name"],
                    program["program_type"],
                    program.get("start_date") or None,
                    program.get("end_date") or None,
                    program.get("official_url") or None,
                    program.get("description") or None,
                    program["public_flag"]
                )
            )

            program_id = cur.fetchone()["program_id"]

        conn.commit()

        return program_id

    finally:
        conn.close()


def update_program(program_id, program):
    """
    番組更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_oshi_program

                SET
                    program_name = %s,
                    program_type = %s,
                    start_date = %s,
                    end_date = %s,
                    official_url = %s,
                    description = %s,
                    public_flag = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    program_id = %s
                """,
                (
                    program["program_name"],
                    program["program_type"],
                    program.get("start_date") or None,
                    program.get("end_date") or None,
                    program.get("official_url") or None,
                    program.get("description") or None,
                    program["public_flag"],
                    program_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_program(program_id):
    """
    番組論理削除
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_oshi_program

                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    program_id = %s
                """,
                (program_id,)
            )

        conn.commit()

    finally:
        conn.close()
