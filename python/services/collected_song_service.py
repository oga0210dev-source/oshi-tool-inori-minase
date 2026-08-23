from python.core.database import get_connection


def get_song_collection_summary(user_id, mode="live"):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            if mode == "all":
                song_type_condition = ""
            else:
                song_type_condition = """
                    AND s.song_type = 'INORI'
                """

            if mode == "live":
                event_type_condition = """
                    st.event_type = 'LIVE'
                """
            else:
                event_type_condition = """
                    st.event_type IN ('LIVE', 'CHOMIN')
                """

            cur.execute(
                f"""
                SELECT
                    COUNT(DISTINCT s.song_group_id) AS count
                FROM m_song s
                WHERE
                    s.is_public = TRUE
                    AND s.is_deleted = FALSE
                    {song_type_condition}
                """
            )

            total_count = cur.fetchone()["count"]

            cur.execute(
                f"""
                SELECT
                    COUNT(DISTINCT st.song_id) AS count
                FROM t_live_user u
                INNER JOIN m_live l
                    ON l.live_id = u.live_id
                INNER JOIN m_setlist st
                    ON {event_type_condition}
                    AND st.event_id = l.live_id
                INNER JOIN m_song s
                    ON s.song_group_id = st.song_id
                WHERE
                    u.user_id = %s
                    AND u.is_join = TRUE
                    AND s.is_public = TRUE
                    AND s.is_deleted = FALSE
                    {song_type_condition}
                """,
                (user_id,)
            )

            collected_count = cur.fetchone()["count"]

            uncollected_count = (
                total_count - collected_count
            )

            if total_count == 0:
                collection_rate = 0
            else:
                collection_rate = round(
                    collected_count / total_count * 100,
                    1
                )

            return {
                "collected_count": collected_count,
                "uncollected_count": uncollected_count,
                "collection_rate": collection_rate
            }

    finally:
        conn.close()


def get_collected_song_list(user_id, mode="live"):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            if mode == "all":
                song_type_condition = ""
            else:
                song_type_condition = """
                    AND s.song_type = 'INORI'
                """

            if mode == "live":
                event_type_condition = """
                    st.event_type = 'LIVE'
                """
            else:
                event_type_condition = """
                    st.event_type IN ('LIVE', 'CHOMIN')
                """

            cur.execute(
                f"""
                SELECT
                    s.song_group_id,
                    MIN(s.song_name) AS song_name,
                    MIN(s.youtube_url) AS youtube_url,
                    MIN(s.apple_music_url) AS apple_music_url,
                    MIN(s.spotify_url) AS spotify_url,
                    COUNT(DISTINCT st.event_id) AS listen_count
                FROM t_live_user u
                INNER JOIN m_live l
                    ON l.live_id = u.live_id
                INNER JOIN m_setlist st
                    ON {event_type_condition}
                    AND st.event_id = l.live_id
                INNER JOIN m_song s
                    ON s.song_group_id = st.song_id
                WHERE
                    u.user_id = %s
                    AND u.is_join = TRUE
                    AND s.is_public = TRUE
                    AND s.is_deleted = FALSE
                    {song_type_condition}
                GROUP BY
                    s.song_group_id
                ORDER BY
                    listen_count DESC,
                    MIN(s.song_name)
                """,
                (user_id,)
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_uncollected_song_list(user_id, mode="live"):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            if mode == "all":
                song_type_condition = ""
            else:
                song_type_condition = """
                    AND s.song_type = 'INORI'
                """

            if mode == "live":
                event_type_condition = """
                    st.event_type = 'LIVE'
                """
            else:
                event_type_condition = """
                    st.event_type IN ('LIVE', 'CHOMIN')
                """

            cur.execute(
                f"""
                SELECT
                    s.song_group_id,
                    MIN(s.song_name) AS song_name,
                    MIN(s.youtube_url) AS youtube_url,
                    MIN(s.apple_music_url) AS apple_music_url,
                    MIN(s.spotify_url) AS spotify_url
                FROM m_song s
                WHERE
                    s.is_public = TRUE
                    AND s.is_deleted = FALSE
                    {song_type_condition}
                    AND NOT EXISTS (
                        SELECT 1
                        FROM t_live_user u
                        INNER JOIN m_setlist st
                            ON {event_type_condition}
                            AND st.event_id = u.live_id
                        WHERE
                            u.user_id = %s
                            AND u.is_join = TRUE
                            AND st.song_id = s.song_group_id
                    )
                GROUP BY
                    s.song_group_id
                ORDER BY
                    MIN(s.song_name)
                """,
                (user_id,)
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_live_appearance_song_list(mode="live"):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            if mode == "all":
                song_type_condition = ""
            else:
                song_type_condition = """
                    AND s.song_type = 'INORI'
                """

            if mode == "live":
                event_type_condition = """
                    st.event_type = 'LIVE'
                """
            else:
                event_type_condition = """
                    st.event_type IN ('LIVE', 'CHOMIN')
                """

            cur.execute(
                f"""
                SELECT
                    s.song_group_id,
                    MIN(s.song_name) AS song_name,
                    MIN(s.youtube_url) AS youtube_url,
                    MIN(s.apple_music_url) AS apple_music_url,
                    MIN(s.spotify_url) AS spotify_url,
                    COUNT(DISTINCT st.event_id) AS appearance_count
                FROM m_setlist st
                INNER JOIN m_song s
                    ON s.song_group_id = st.song_id
                WHERE
                    {event_type_condition}
                    AND s.is_public = TRUE
                    AND s.is_deleted = FALSE
                    {song_type_condition}
                GROUP BY
                    s.song_group_id
                ORDER BY
                    appearance_count DESC,
                    MIN(s.song_name)
                """
            )

            return cur.fetchall()

    finally:
        conn.close()
