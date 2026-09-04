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
            s.medley_order,
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
            s.medley_order,
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
                        is_medley,
                        medley_order
                    )
                    VALUES
                    (
                        %s,%s,%s,%s,%s,%s
                    )
                    """,
                    (
                        event_type,
                        event_id,
                        item["song_id"],
                        item["song_order"],
                        item["is_medley"],
                        item.get("medley_order")
                    )
                )

        conn.commit()

    finally:
        conn.close()


def get_setlist_ai_history():
    """
    AIセトリ予測用の過去LIVEセトリを取得

    対象:
        - LIVEのみ
        - 削除されていないLIVE
        - 公開されているLIVE
        - INORI楽曲のみ
        - セトリ登録済みの楽曲

    町民集会は対象外。
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    l.live_id,
                    l.live_date,
                    l.live_name,
                    l.tour_name,
                    l.tour_order,
                    s.song_group_id,
                    s.song_name,
                    s.album_name,
                    ms.song_order,
                    ms.is_medley,
                    ms.medley_order
                FROM m_setlist ms
                INNER JOIN m_live l
                    ON ms.event_id = l.live_id
                INNER JOIN m_song s
                    ON ms.song_id = s.song_group_id
                WHERE
                    ms.event_type = 'LIVE'
                    AND l.is_deleted = FALSE
                    AND l.public_flag = TRUE
                    AND s.song_type = 'INORI'
                ORDER BY
                    l.live_date ASC,
                    l.live_id ASC,
                    ms.song_order ASC,
                    ms.medley_order ASC NULLS LAST
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "live_id": row["live_id"],
                    "live_date": row["live_date"],
                    "live_name": row["live_name"],
                    "tour_name": row["tour_name"],
                    "tour_order": row["tour_order"],
                    "song_id": row["song_group_id"],
                    "song_name": row["song_name"],
                    "album_name": row["album_name"],
                    "song_order": row["song_order"],
                    "is_medley": row["is_medley"],
                    "medley_order": row["medley_order"]
                }
                for row in rows
            ]

    finally:
        conn.close()
