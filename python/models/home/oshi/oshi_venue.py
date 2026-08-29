from python.core.database import get_connection


def get_oshi_venue_list(
        keyword="",
        sort="name"
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            conditions = [
                "v.is_deleted = FALSE",
                "v.public_flag = TRUE",
                "v.prefecture_code IS NOT NULL",
                "v.prefecture_code <> 0"
            ]

            params = []

            if keyword:
                conditions.append(
                    """
                    (
                        v.venue_name ILIKE %s
                        OR v.address ILIKE %s
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
                "name": """
                    v.venue_name ASC,
                    v.venue_id ASC
                """,

                "prefecture": """
                    v.prefecture_code ASC,
                    v.venue_name ASC,
                    v.venue_id ASC
                """,

                "capacity": """
                    v.capacity DESC NULLS LAST,
                    v.venue_name ASC,
                    v.venue_id ASC
                """
            }

            order_sql = sort_map.get(
                sort,
                sort_map["name"]
            )

            cur.execute(
                f"""
                SELECT
                    v.venue_id,
                    v.venue_name,
                    v.address,
                    v.prefecture_code,
                    p.prefecture_name,
                    v.latitude,
                    v.longitude,
                    v.capacity,
                    v.official_url

                FROM m_venue v

                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code

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


def get_oshi_venue(
        venue_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    v.venue_id,
                    v.venue_name,
                    v.address,
                    v.prefecture_code,
                    p.prefecture_name,
                    v.latitude,
                    v.longitude,
                    v.capacity,
                    v.official_url

                FROM m_venue v

                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code

                WHERE
                    v.venue_id = %s
                    AND v.is_deleted = FALSE
                    AND v.public_flag = TRUE
                    AND v.prefecture_code IS NOT NULL
                    AND v.prefecture_code <> 0
                """,
                (venue_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def get_oshi_venue_event_list(
        venue_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    event_type,
                    event_id,
                    event_name,
                    event_date,
                    tour_name,
                    performance_type,
                    capacity

                FROM (
                    /*
                     * ライブ
                     */
                    SELECT
                        'LIVE' AS event_type,
                        l.live_id AS event_id,
                        l.live_name AS event_name,
                        l.live_date AS event_date,
                        l.tour_name AS tour_name,
                        NULL AS performance_type,
                        v.capacity AS capacity

                    FROM m_live l

                    LEFT JOIN m_venue v
                        ON l.venue_id = v.venue_id

                    WHERE
                        l.venue_id = %s
                        AND l.is_deleted = FALSE
                        AND l.public_flag = TRUE


                    UNION ALL


                    /*
                     * 町民集会
                     */
                    SELECT
                        'MEETING' AS event_type,
                        m.meeting_id AS event_id,
                        m.meeting_name AS event_name,
                        m.meeting_date AS event_date,
                        m.meeting_name AS tour_name,
                        m.performance_type AS performance_type,
                        v.capacity AS capacity

                    FROM m_meeting m

                    LEFT JOIN m_venue v
                        ON m.venue_id = v.venue_id

                    WHERE
                        m.venue_id = %s
                        AND m.is_deleted = FALSE
                        AND m.public_flag = TRUE

                ) events

                ORDER BY
                    event_date ASC NULLS LAST,
                    event_type ASC,
                    event_id ASC
                """,
                (
                    venue_id,
                    venue_id
                )
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_oshi_venue_tour_capacity(
        tour_name
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    l.live_id,
                    l.live_name,
                    l.live_date,
                    l.venue_id,
                    v.venue_name,
                    v.capacity

                FROM m_live l

                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id

                WHERE
                    l.tour_name = %s
                    AND l.is_deleted = FALSE
                    AND l.public_flag = TRUE

                ORDER BY
                    l.live_date ASC,
                    l.live_id ASC
                """,
                (tour_name,)
            )

            lives = cur.fetchall()

            total_capacity = sum(
                live["capacity"]
                for live in lives
                if live["capacity"] is not None
            )

            # JSONで扱える形式に変換
            for live in lives:
                if live["live_date"] is not None:
                    live["live_date"] = (
                        live["live_date"].isoformat()
                    )

            return {
                "tour_name": tour_name,
                "total_capacity": total_capacity,
                "lives": lives
            }

    finally:
        conn.close()


def get_oshi_venue_meeting_capacity(
        meeting_name
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    m.meeting_id AS event_id,
                    m.meeting_name AS event_name,
                    m.meeting_date AS event_date,
                    m.performance_type,
                    m.venue_id,
                    v.venue_name,
                    v.capacity
                FROM m_meeting m
                LEFT JOIN m_venue v
                    ON m.venue_id = v.venue_id
                WHERE
                    m.meeting_name = %s
                    AND m.is_deleted = FALSE
                    AND m.public_flag = TRUE
                ORDER BY
                    m.meeting_date ASC,
                    m.meeting_id ASC
                """,
                (meeting_name,)
            )

            meetings = cur.fetchall()

            total_capacity = sum(
                meeting["capacity"]
                for meeting in meetings
                if meeting["capacity"] is not None
            )

            for meeting in meetings:
                if meeting["event_date"] is not None:
                    meeting["event_date"] = (
                        meeting["event_date"].isoformat()
                    )

            return {
                "name": meeting_name,
                "total_capacity": total_capacity,
                "events": meetings
            }

    finally:
        conn.close()
