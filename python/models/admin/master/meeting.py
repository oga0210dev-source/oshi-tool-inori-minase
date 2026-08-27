from python.core.database import get_connection


def get_meeting_list(keyword=None, sort="date"):
    conn = get_connection()

    if sort == "date_desc":
        order_by = """
            meeting_date DESC
        """

    elif sort == "date_asc":
        order_by = """
            meeting_date ASC
        """

    elif sort == "name":
        order_by = """
            meeting_name ASC
        """

    elif sort == "updated":
        order_by = """
            m_meeting.updated_at DESC
        """

    else:
        order_by = """
            meeting_date ASC
        """

    sql = """
        SELECT
            m_meeting.meeting_id,
            m_meeting.meeting_name,
            m_meeting.meeting_date,
            m_meeting.performance_type,
            m_venue.venue_name,
            m_venue.prefecture_code,
            m_prefecture.prefecture_name,
            m_meeting.official_url,
            m_meeting.public_flag,
            m_meeting.created_at,
            m_meeting.updated_at

        FROM m_meeting

        LEFT JOIN m_venue
        ON m_meeting.venue_id = m_venue.venue_id

        LEFT JOIN m_prefecture
        ON m_venue.prefecture_code = m_prefecture.prefecture_code

        WHERE
            m_meeting.is_deleted = FALSE
    """

    params = []

    if keyword:
        sql += """
            AND (
                m_meeting.meeting_name ILIKE %s
                OR m_venue.venue_name ILIKE %s
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
            cur.execute(
                sql,
                params
            )
            return cur.fetchall()

    finally:
        conn.close()


def get_meeting(meeting_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m_meeting.*,
                    m_venue.venue_name,
                    m_venue.prefecture_code,
                    m_prefecture.prefecture_name

                FROM m_meeting

                LEFT JOIN m_venue
                ON m_meeting.venue_id = m_venue.venue_id

                LEFT JOIN m_prefecture
                ON m_venue.prefecture_code = m_prefecture.prefecture_code

                WHERE
                    m_meeting.meeting_id = %s
                    AND m_meeting.is_deleted = FALSE
                """,
                (meeting_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def create_meeting(meeting):
    """
    町民集会登録
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_meeting(
                    meeting_name,
                    meeting_date,
                    performance_type,
                    venue_id,
                    official_url,
                    public_flag
                )

                VALUES(
                    %s,%s,%s,%s,%s,%s
                )

                RETURNING meeting_id
                """,
                (
                    meeting["meeting_name"],
                    meeting["meeting_date"],
                    meeting["performance_type"],
                    meeting["venue_id"],
                    meeting["official_url"],
                    meeting["public_flag"]
                )
            )

            meeting_id = cur.fetchone()["meeting_id"]

        conn.commit()

        return meeting_id

    finally:
        conn.close()


def update_meeting(meeting_id, meeting):
    """
    町民集会更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_meeting
                SET
                    meeting_name = %s,
                    meeting_date = %s,
                    performance_type = %s,
                    venue_id = %s,
                    official_url = %s,
                    public_flag = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    meeting_id = %s
                """,
                (
                    meeting["meeting_name"],
                    meeting["meeting_date"],
                    meeting["performance_type"],
                    meeting["venue_id"],
                    meeting["official_url"],
                    meeting["public_flag"],
                    meeting_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_meeting(meeting_id):
    """
    町民集会論理削除
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_meeting
                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    meeting_id = %s
                """,
                (meeting_id,)
            )

        conn.commit()

    finally:
        conn.close()


def get_meeting_guests(meeting_id):
    """
    町民集会のゲスト一覧取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    guest_id,
                    meeting_id,
                    guest_name,
                    display_order,
                    created_at,
                    updated_at

                FROM m_meeting_guest

                WHERE
                    meeting_id = %s
                    AND is_deleted = FALSE

                ORDER BY
                    display_order ASC,
                    guest_id ASC
                """,
                (meeting_id,)
            )

            return cur.fetchall()


    finally:
        conn.close()


def create_meeting_guest(meeting_id, guest_name, display_order=0):
    """
    町民集会ゲスト登録
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO m_meeting_guest(
                    meeting_id,
                    guest_name,
                    display_order
                )

                VALUES(
                    %s,
                    %s,
                    %s
                )

                RETURNING guest_id
                """,
                (
                    meeting_id,
                    guest_name,
                    display_order
                )
            )

            guest_id = cur.fetchone()["guest_id"]

        conn.commit()

        return guest_id

    finally:
        conn.close()


def update_meeting_guest(
        guest_id,
        guest_name,
        display_order=0
):
    """
    町民集会ゲスト更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_meeting_guest

                SET
                    guest_name = %s,
                    display_order = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    guest_id = %s
                    AND is_deleted = FALSE
                """,
                (
                    guest_name,
                    display_order,
                    guest_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_meeting_guest(guest_id):
    """
    町民集会ゲスト論理削除
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_meeting_guest

                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    guest_id = %s
                """,
                (guest_id,)
            )

        conn.commit()

    finally:
        conn.close()
