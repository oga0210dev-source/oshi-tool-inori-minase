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

    elif sort == "updated":
        order_by = """
            updated_at DESC
        """

    else:
        order_by = """
            CASE
                WHEN song_type = 'INORI' THEN 0
                WHEN song_type = 'OTHER' THEN 1
                ELSE 2
            END ASC,
            CASE
                WHEN song_type = 'INORI' THEN release_date
                ELSE NULL
            END DESC NULLS LAST,
            display_order
        """

    sql = """
        SELECT
            song_id,
            song_group_id,
            song_name,
            song_type,
            album_name,
            release_date,
            display_order,
            lyricist,
            composer,
            arranger,
            tie_up,
            youtube_url,
            apple_music_url,
            spotify_url,
            is_public,
            created_at,
            updated_at

        FROM m_song

        WHERE
            is_deleted = FALSE
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
            cur.execute(
                sql,
                params
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_song(song_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM m_song

                WHERE
                    song_id = %s
                """,
                (song_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def get_song_groups():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    song_group_id,
                    song_name,
                    song_type,
                    release_date,
                    album_name,
                    display_order

                FROM m_song

                WHERE
                    song_id = song_group_id
                    AND is_deleted = FALSE

                ORDER BY
                    CASE
                        WHEN song_type = 'INORI' THEN 1
                        WHEN song_type = 'OTHER' THEN 2
                        ELSE 3
                    END,
                    release_date ASC NULLS LAST,
                    album_name ASC NULLS LAST,
                    display_order ASC NULLS LAST,
                    song_name ASC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_song_by_group(song_group_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    song_name,
                    lyricist,
                    composer,
                    arranger,
                    tie_up,
                    youtube_url,
                    apple_music_url,
                    spotify_url

                FROM m_song

                WHERE
                    song_group_id = %s
                    AND is_deleted = FALSE

                ORDER BY
                    song_id ASC

                LIMIT 1
                """,
                (song_group_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def exists_song(song_name, album_name, song_id=None):
    conn = get_connection()

    sql = """
        SELECT
            COUNT(*) AS count

        FROM m_song

        WHERE
            song_name = %s
            AND album_name = %s
            AND is_deleted = FALSE
    """

    params = [
        song_name,
        album_name
    ]

    if song_id:
        sql += """
            AND song_id <> %s
        """

        params.append(song_id)

    try:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                params
            )

            return cur.fetchone()["count"] > 0

    finally:
        conn.close()


def create_song(song):
    """
    曲登録
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # song_id取得
            cur.execute(
                """
                SELECT nextval(
                    pg_get_serial_sequence('m_song', 'song_id')
                ) AS song_id
                """
            )

            song_id = cur.fetchone()["song_id"]

            # 同一曲グループ
            song_group_id = song["song_group_id"]

            if not song_group_id:
                song_group_id = song_id

            # 表示順を自動設定
            if not song["album_name"]:

                display_order = 1

            else:

                cur.execute(
                    """
                    SELECT
                        COALESCE(
                            MAX(display_order),
                            0
                        ) + 1 AS display_order

                    FROM m_song

                    WHERE
                        is_deleted = FALSE
                        AND album_name = %s
                    """,
                    (song["album_name"],)
                )

                display_order = cur.fetchone()["display_order"]

            cur.execute(
                """
                INSERT INTO m_song(
                    song_id,
                    song_group_id,
                    song_name,
                    song_type,
                    release_date,
                    album_name,
                    display_order,
                    lyricist,
                    composer,
                    arranger,
                    tie_up,
                    youtube_url,
                    apple_music_url,
                    spotify_url,
                    is_public
                )

                VALUES(
                    %s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s
                )
                """,
                (
                    song_id,
                    song_group_id,
                    song["song_name"],
                    song["song_type"],
                    song["release_date"],
                    song["album_name"],
                    display_order,
                    song["lyricist"],
                    song["composer"],
                    song["arranger"],
                    song["tie_up"],
                    song["youtube_url"],
                    song["apple_music_url"],
                    song["spotify_url"],
                    song["is_public"]
                )
            )

        conn.commit()

        return song_id

    finally:
        conn.close()


def update_song(song_id, song):
    """
    曲更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_song

                SET
                    song_group_id = %s,
                    song_name = %s,
                    song_type = %s,
                    release_date = %s,
                    album_name = %s,
                    display_order = %s,
                    lyricist = %s,
                    composer = %s,
                    arranger = %s,
                    tie_up = %s,
                    youtube_url = %s,
                    apple_music_url = %s,
                    spotify_url = %s,
                    is_public = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    song_id = %s
                """,
                (
                    song["song_group_id"],
                    song["song_name"],
                    song["song_type"],
                    song["release_date"],
                    song["album_name"],
                    song["display_order"],
                    song["lyricist"],
                    song["composer"],
                    song["arranger"],
                    song["tie_up"],
                    song["youtube_url"],
                    song["apple_music_url"],
                    song["spotify_url"],
                    song["is_public"],
                    song_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def delete_song(song_id):
    """
    曲論理削除
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE m_song

                SET
                    is_deleted = TRUE,
                    updated_at = CURRENT_TIMESTAMP

                WHERE
                    song_id = %s
                """,
                (song_id,)
            )

        conn.commit()

    finally:
        conn.close()
