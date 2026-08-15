from python.services.discord_service import send_inquiry_notification


def create_inquiry(
    conn,
    user_id,
    inquiry_type,
    subject,
    email,
    message
):
    if inquiry_type == "INQUIRY" and not email:
        raise ValueError("問い合わせの場合はメールアドレスが必須です。")

    sql = """
        INSERT INTO t_inquiry (
            user_id,
            inquiry_type,
            subject,
            email,
            message
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING inquiry_id
    """

    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                user_id,
                inquiry_type,
                subject,
                email if inquiry_type == "INQUIRY" else None,
                message
            )
        )
        inquiry_id = cur.fetchone()["inquiry_id"]

    conn.commit()

    send_inquiry_notification(
        inquiry_id=inquiry_id,
        inquiry_type=inquiry_type,
        subject=subject,
        message=message,
        user_id=user_id,
        email=email if inquiry_type == "INQUIRY" else None
    )

    return inquiry_id


def get_inquiry_list(conn, status="", inquiry_type=""):
    sql = """
        SELECT
            i.inquiry_id,
            i.user_id,
            u.user_name,
            i.inquiry_type,
            i.subject,
            i.email,
            i.status,
            i.created_at,
            i.updated_at
        FROM t_inquiry i
        LEFT JOIN m_user u
            ON u.user_id = i.user_id
        WHERE 1 = 1
    """

    params = []

    if status in ("UNRESOLVED", "IN_PROGRESS", "RESOLVED"):
        sql += " AND i.status = %s"
        params.append(status)

    if inquiry_type in ("INQUIRY", "REQUEST", "BUG"):
        sql += " AND i.inquiry_type = %s"
        params.append(inquiry_type)

    sql += """
        ORDER BY
            CASE i.status
                WHEN 'UNRESOLVED' THEN 1
                WHEN 'IN_PROGRESS' THEN 2
                WHEN 'RESOLVED' THEN 3
                ELSE 4
            END,
            i.created_at DESC
    """

    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def get_inquiry_detail(conn, inquiry_id):
    sql = """
        SELECT
            i.inquiry_id,
            i.user_id,
            u.user_name,
            i.inquiry_type,
            i.subject,
            i.email,
            i.message,
            i.status,
            i.admin_memo,
            i.created_at,
            i.updated_at
        FROM t_inquiry i
        LEFT JOIN m_user u
            ON u.user_id = i.user_id
        WHERE i.inquiry_id = %s
    """

    with conn.cursor() as cur:
        cur.execute(sql, (inquiry_id,))
        return cur.fetchone()


def update_inquiry(
    conn,
    inquiry_id,
    status,
    admin_memo
):
    sql = """
        UPDATE t_inquiry
        SET
            status = %s,
            admin_memo = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE inquiry_id = %s
    """

    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                status,
                admin_memo,
                inquiry_id
            )
        )

    conn.commit()


def get_active_todos(conn):
    sql = """
        SELECT
            inquiry_id,
            inquiry_type,
            subject,
            message,
            status,
            created_at
        FROM t_inquiry
        WHERE status IN ('UNRESOLVED', 'IN_PROGRESS')
        ORDER BY
            CASE status
                WHEN 'UNRESOLVED' THEN 1
                WHEN 'IN_PROGRESS' THEN 2
                ELSE 3
            END,
            created_at ASC
    """

    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()
