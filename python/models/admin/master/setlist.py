from python.core.database import get_connection


def get_setlist_list(event_type=None, event_id=None):
    conn = get_connection()

    sql = """
        SELECT
            s.event_type,
            s.event_id,
            s.song_id,
            s.song_order,
            s.is_medley,
            MIN(m.song_name) AS song_name,
            MIN(m.album_name) AS album_name,
            s.created_at,
            s.updated_at
        FROM m_setlist s
        INNER JOIN m_song m
        ON s.song_id = m.song_group_id
        WHERE 1=1
    """

    params = []

    if event_type:
        sql += " AND s.event_type=%s"
        params.append(event_type)

    if event_id:
        sql += " AND s.event_id=%s"
        params.append(event_id)

    sql += """
        GROUP BY
            s.event_type,
            s.event_id,
            s.song_id,
            s.song_order,
            s.is_medley,
            s.created_at,
            s.updated_at
        ORDER BY
            s.song_order
    """

    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def save_setlist(event_type, event_id, setlist):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            # 一旦削除
            cur.execute(
                """
                DELETE FROM m_setlist
                WHERE event_type=%s
                AND event_id=%s
                """,
                (
                    event_type,
                    event_id
                )
            )

            for item in setlist:
                cur.execute(
                    # m_setlist.song_idにはm_song.song_group_idを保存
                    """
                    INSERT INTO m_setlist
                    (
                        event_type,
                        event_id,
                        song_id,
                        song_order,
                        is_medley
                    )
                    VALUES
                    (
                        %s,%s,%s,%s,%s
                    )
                    """,
                    (
                        event_type,
                        event_id,
                        item["song_id"],
                        item["song_order"],
                        item["is_medley"]
                    )
                )

        conn.commit()

    finally:
        conn.close()
