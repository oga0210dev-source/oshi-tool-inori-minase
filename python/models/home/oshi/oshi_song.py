from python.core.database import get_connection


def get_song_list(keyword=None, sort="album"):
    conn = get_connection()

    if sort == "song":
        order_by = """
            song_name ASC
        """
    elif sort == "release_desc":
        order_by = """
            release_date DESC NULLS FIRST,
            album_name ASC,
            display_order ASC,
            song_name ASC
        """
    elif sort == "release_asc":
        order_by = """
            release_date ASC NULLS LAST,
            album_name ASC,
            display_order ASC,
            song_name ASC
        """
    else:
        order_by = """
            release_date DESC NULLS FIRST,
            album_name ASC,
            display_order ASC,
            song_name ASC
        """

    sql = """
        SELECT
            song_id,
            song_name,
            album_name,
            release_date,
            display_order,
            lyricist,
            composer,
            arranger,
            tie_up,
            youtube_url,
            apple_music_url,
            spotify_url
        FROM m_song
        WHERE
            is_deleted = FALSE
            AND is_public = TRUE
            AND song_type = 'INORI'
    """

    params = []

    if keyword:
        sql += """
            AND (
                song_name ILIKE %s
                OR album_name ILIKE %s
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
