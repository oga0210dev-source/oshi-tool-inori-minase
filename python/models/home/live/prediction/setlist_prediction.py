from python.core.database import get_connection


def get_setlist_prediction_list(user_id, tour_name=None):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            sql = """
                SELECT
                    p.prediction_id,
                    p.live_id,
                    l.live_name,
                    l.tour_name,
                    l.live_date,
                    l.venue_name,
                    pref.prefecture_name,
                    CASE
                        WHEN l.live_date <= CURRENT_DATE THEN TRUE
                        ELSE FALSE
                    END AS is_finished
                FROM t_setlist_prediction p
                INNER JOIN m_live l
                    ON p.live_id = l.live_id
                LEFT JOIN m_prefecture pref
                    ON l.prefecture_code = pref.prefecture_code
                WHERE p.user_id = %s
                  AND l.is_deleted = FALSE
            """

            params = [user_id]

            if tour_name:
                sql += " AND l.tour_name ILIKE %s"
                params.append(f"%{tour_name}%")

            sql += """
                ORDER BY
                    l.live_date ASC,
                    l.tour_order ASC,
                    p.prediction_id ASC
            """

            cur.execute(sql, params)
            return cur.fetchall()

    finally:
        conn.close()


def get_setlist_prediction_live_list(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    l.live_id,
                    l.live_name,
                    l.tour_name,
                    l.live_date,
                    l.venue_name,
                    pref.prefecture_name
                FROM m_live l
                LEFT JOIN m_prefecture pref
                    ON l.prefecture_code = pref.prefecture_code
                WHERE l.is_deleted = FALSE
                  AND l.live_date >= CURRENT_DATE
                  AND NOT EXISTS (
                      SELECT 1
                      FROM t_setlist_prediction p
                      WHERE p.user_id = %s
                        AND p.live_id = l.live_id
                  )
                ORDER BY
                    l.live_date ASC,
                    l.tour_order ASC,
                    l.live_id ASC
                """,
                (user_id,)
            )
            return cur.fetchall()

    finally:
        conn.close()


def get_setlist_prediction_live(live_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    l.live_id,
                    l.live_name,
                    l.tour_name,
                    l.tour_order,
                    l.live_date,
                    l.venue_name,
                    l.prefecture_code,
                    l.official_url,
                    pref.prefecture_name
                FROM m_live l
                LEFT JOIN m_prefecture pref
                    ON l.prefecture_code = pref.prefecture_code
                WHERE l.live_id = %s
                  AND l.is_deleted = FALSE
                """,
                (live_id,)
            )
            return cur.fetchone()

    finally:
        conn.close()


def get_setlist_prediction_song_groups():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    song_group_id,
                    MIN(song_name) AS song_name
                FROM m_song
                WHERE is_deleted = FALSE
                  AND is_public = TRUE
                GROUP BY song_group_id
                ORDER BY
                    MIN(display_order),
                    MIN(song_id)
                """
            )
            return cur.fetchall()

    finally:
        conn.close()


def save_setlist_prediction(user_id, live_id, songs):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT prediction_id
                FROM t_setlist_prediction
                WHERE user_id = %s
                  AND live_id = %s
                """,
                (user_id, live_id)
            )

            existing = cur.fetchone()

            if existing:
                prediction_id = existing["prediction_id"]

                cur.execute(
                    """
                    DELETE FROM t_setlist_prediction_song
                    WHERE prediction_id = %s
                    """,
                    (prediction_id,)
                )

                cur.execute(
                    """
                    DELETE FROM t_setlist_prediction
                    WHERE prediction_id = %s
                    """,
                    (prediction_id,)
                )

            cur.execute(
                """
                INSERT INTO t_setlist_prediction (
                    user_id,
                    live_id
                )
                VALUES (%s, %s)
                RETURNING prediction_id
                """,
                (user_id, live_id)
            )

            prediction_id = cur.fetchone()["prediction_id"]

            for song in songs:
                cur.execute(
                    """
                    INSERT INTO t_setlist_prediction_song (
                        prediction_id,
                        song_id,
                        song_order,
                        is_medley,
                        medley_order
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        prediction_id,
                        song["song_id"],
                        song["song_order"],
                        song["is_medley"],
                        song["medley_order"]
                    )
                )

        conn.commit()
        return prediction_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_setlist_prediction(prediction_id, user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.prediction_id,
                    p.user_id,
                    p.live_id,
                    l.live_name,
                    l.tour_name,
                    l.tour_order,
                    l.live_date,
                    l.venue_name,
                    l.prefecture_code,
                    l.official_url,
                    pref.prefecture_name
                FROM t_setlist_prediction p
                INNER JOIN m_live l
                    ON p.live_id = l.live_id
                LEFT JOIN m_prefecture pref
                    ON l.prefecture_code = pref.prefecture_code
                WHERE p.prediction_id = %s
                  AND p.user_id = %s
                  AND l.is_deleted = FALSE
                """,
                (prediction_id, user_id)
            )

            prediction = cur.fetchone()

            if not prediction:
                return None, []

            cur.execute(
                """
                SELECT
                    ps.song_id,
                    ps.song_order,
                    ps.is_medley,
                    ps.medley_order,
                    s.song_name,
                    s.album_name,
                    s.youtube_url,
                    s.apple_music_url,
                    s.spotify_url
                FROM t_setlist_prediction_song ps
                INNER JOIN m_song s
                    ON ps.song_id = s.song_id
                WHERE ps.prediction_id = %s
                  AND s.is_deleted = FALSE
                  AND s.is_public = TRUE
                ORDER BY ps.song_order ASC
                """,
                (prediction_id,)
            )

            songs = cur.fetchall()

            return prediction, songs

    finally:
        conn.close()


def update_setlist_prediction(prediction_id, user_id, songs):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT prediction_id
                FROM t_setlist_prediction
                WHERE prediction_id = %s
                  AND user_id = %s
                """,
                (prediction_id, user_id)
            )

            if not cur.fetchone():
                return False

            cur.execute(
                """
                DELETE FROM t_setlist_prediction_song
                WHERE prediction_id = %s
                """,
                (prediction_id,)
            )

            for song in songs:
                cur.execute(
                    """
                    INSERT INTO t_setlist_prediction_song (
                        prediction_id,
                        song_id,
                        song_order,
                        is_medley,
                        medley_order
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        prediction_id,
                        song["song_id"],
                        song["song_order"],
                        song["is_medley"],
                        song["medley_order"]
                    )
                )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def delete_setlist_prediction(prediction_id, user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT prediction_id
                FROM t_setlist_prediction
                WHERE prediction_id = %s
                  AND user_id = %s
                """,
                (prediction_id, user_id)
            )

            prediction = cur.fetchone()

            if not prediction:
                return False

            cur.execute(
                """
                DELETE FROM t_setlist_prediction_song
                WHERE prediction_id = %s
                """,
                (prediction_id,)
            )

            cur.execute(
                """
                DELETE FROM t_setlist_prediction
                WHERE prediction_id = %s
                """,
                (prediction_id,)
            )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_public_setlist_prediction(prediction_id):
    """
    共有ページ用の予測セトリ取得。

    ログインユーザーのチェックは行わず、
    prediction_id が存在し、ライブが削除されていなければ
    誰でも閲覧できるデータとして取得する。
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.prediction_id,
                    p.user_id,
                    p.live_id,
                    l.live_name,
                    l.tour_name,
                    l.tour_order,
                    l.live_date,
                    l.venue_name,
                    l.prefecture_code,
                    l.official_url,
                    pref.prefecture_name
                FROM t_setlist_prediction p
                INNER JOIN m_live l
                    ON p.live_id = l.live_id
                LEFT JOIN m_prefecture pref
                    ON l.prefecture_code = pref.prefecture_code
                WHERE p.prediction_id = %s
                  AND l.is_deleted = FALSE
                """,
                (prediction_id,)
            )

            prediction = cur.fetchone()

            if not prediction:
                return None, []

            cur.execute(
                """
                SELECT
                    ps.song_id,
                    ps.song_order,
                    ps.is_medley,
                    ps.medley_order,
                    s.song_name,
                    s.album_name,
                    s.youtube_url,
                    s.apple_music_url,
                    s.spotify_url
                FROM t_setlist_prediction_song ps
                INNER JOIN m_song s
                    ON ps.song_id = s.song_id
                WHERE ps.prediction_id = %s
                  AND s.is_deleted = FALSE
                  AND s.is_public = TRUE
                ORDER BY ps.song_order ASC
                """,
                (prediction_id,)
            )

            songs = cur.fetchall()

            return prediction, songs

    finally:
        conn.close()
