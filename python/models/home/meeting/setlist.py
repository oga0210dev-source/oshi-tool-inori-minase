from python.core.database import get_connection


def get_meeting_info(meeting_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    meeting_id,
                    meeting_name,
                    meeting_date,
                    performance_type
                FROM m_meeting
                WHERE
                    meeting_id = %s
                    AND is_deleted = FALSE
                    AND public_flag = TRUE
                """,
                (meeting_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()


def get_setlist(meeting_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    s.song_order,
                    s.is_medley,
                    s.medley_order,
                    m.song_name,
                    m.album_name,
                    m.youtube_url,
                    m.apple_music_url,
                    m.spotify_url
                FROM m_setlist s
                LEFT JOIN m_song m
                    ON s.song_id = m.song_id
                WHERE
                    s.event_type = 'CHOMIN'
                    AND s.event_id = %s
                ORDER BY
                    s.song_order,
                    s.medley_order
                """,
                (meeting_id,)
            )
            return cur.fetchall()
    finally:
        conn.close()
