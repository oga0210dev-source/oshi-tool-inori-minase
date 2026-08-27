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
                    v.venue_name,
                    pref.prefecture_name,
                    CASE
                        WHEN l.live_date <= CURRENT_DATE THEN TRUE
                        ELSE FALSE
                    END AS is_finished
                FROM t_setlist_prediction p
                INNER JOIN m_live l
                    ON p.live_id = l.live_id
                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id
                LEFT JOIN m_prefecture pref
                    ON v.prefecture_code = pref.prefecture_code
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
            predictions = cur.fetchall()

            for prediction in predictions:

                match_rate, partial_match_rate, _, _ = \
                    get_setlist_prediction_match_rate(
                        prediction["prediction_id"]
                    )

                prediction["match_rate"] = match_rate
                prediction["partial_match_rate"] = partial_match_rate

            return predictions

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
                    v.venue_name,
                    pref.prefecture_name
                FROM m_live l
                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id
                LEFT JOIN m_prefecture pref
                    ON v.prefecture_code = pref.prefecture_code
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
                    v.venue_name,
                    v.prefecture_code,
                    l.official_url,
                    pref.prefecture_name
                FROM m_live l
                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id
                LEFT JOIN m_prefecture pref
                    ON v.prefecture_code = pref.prefecture_code
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
                    MIN(s.song_group_id) AS song_group_id,
                    s.song_name
                FROM m_song s
                WHERE s.is_deleted = FALSE
                  AND s.is_public = TRUE
                  AND s.song_type = 'INORI'

                GROUP BY
                    s.song_name

                ORDER BY
                    MIN(s.release_date),
                    MIN(s.display_order)
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
                    v.venue_name,
                    v.prefecture_code,
                    l.official_url,
                    pref.prefecture_name
                FROM t_setlist_prediction p
                INNER JOIN m_live l
                    ON p.live_id = l.live_id
                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id
                LEFT JOIN m_prefecture pref
                    ON v.prefecture_code = pref.prefecture_code
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
                    v.venue_name,
                    v.prefecture_code,
                    l.official_url,
                    pref.prefecture_name,
                    CASE
                        WHEN l.live_date <= CURRENT_DATE THEN TRUE
                        ELSE FALSE
                    END AS is_finished
                FROM t_setlist_prediction p
                INNER JOIN m_live l
                    ON p.live_id = l.live_id
                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id
                LEFT JOIN m_prefecture pref
                    ON v.prefecture_code = pref.prefecture_code
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

            match_rate, partial_match_rate, \
                medley_match_rate, medley_partial_match_rate = \
                get_setlist_prediction_match_rate(prediction_id)

            prediction = dict(prediction)
            prediction["match_rate"] = match_rate
            prediction["partial_match_rate"] = partial_match_rate
            prediction["medley_match_rate"] = medley_match_rate
            prediction["medley_partial_match_rate"] = medley_partial_match_rate

            return prediction, songs

    finally:
        conn.close()


def get_setlist_prediction_match_rate(prediction_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            # 予測からライブIDを取得
            cur.execute(
                """
                SELECT
                    live_id
                FROM t_setlist_prediction
                WHERE prediction_id = %s
                """,
                (prediction_id,)
            )

            prediction = cur.fetchone()

            if not prediction:
                return None, None, None, None

            live_id = prediction["live_id"]

            # 予測セトリ取得
            cur.execute(
                """
                SELECT
                    ps.song_order,
                    ps.is_medley,
                    ps.medley_order,
                    s.song_group_id
                FROM t_setlist_prediction_song ps
                INNER JOIN m_song s
                    ON ps.song_id = s.song_id
                WHERE ps.prediction_id = %s
                  AND s.is_deleted = FALSE
                  AND s.is_public = TRUE
                ORDER BY
                    ps.song_order,
                    ps.medley_order
                """,
                (prediction_id,)
            )

            predicted_songs = cur.fetchall()

            # 実際のライブセトリ取得
            cur.execute(
                """
                SELECT
                    ms.song_order,
                    ms.is_medley,
                    ms.medley_order,
                    s.song_group_id
                FROM m_setlist ms
                INNER JOIN m_song s
                    ON ms.song_id = s.song_id
                WHERE ms.event_type = 'LIVE'
                  AND ms.event_id = %s
                  AND s.is_deleted = FALSE
                  AND s.is_public = TRUE
                ORDER BY
                    ms.song_order,
                    ms.medley_order
                """,
                (live_id,)
            )

            actual_songs = cur.fetchall()

            # 本番セトリがまだ登録されていない
            if not actual_songs:
                return None, None, None, None

            # 予測セトリが空
            if not predicted_songs:
                return 0, 0, 0, 0

            def group_setlist(songs):
                items = []
                medley = None

                for song in songs:

                    if not song["is_medley"]:
                        items.append({
                            "song_order": song["song_order"],
                            "is_medley": False,
                            "songs": [song]
                        })
                        continue

                    if (
                        medley is None
                        or medley["song_order"] != song["song_order"]
                    ):
                        medley = {
                            "song_order": song["song_order"],
                            "is_medley": True,
                            "songs": []
                        }

                        items.append(medley)

                    medley["songs"].append(song)

                return items

            predicted_items = group_setlist(predicted_songs)
            actual_items = group_setlist(actual_songs)

            actual_by_order = {
                item["song_order"]: item
                for item in actual_items
            }

            total_item_count = len(predicted_items)
            match_item_count = 0

            total_song_count = sum(
                len(item["songs"])
                for item in predicted_items
            )
            partial_match_song_count = 0

            total_medley_count = sum(
                1
                for item in predicted_items
                if item["is_medley"]
            )

            match_medley_count = 0

            total_medley_song_count = sum(
                len(item["songs"])
                for item in predicted_items
                if item["is_medley"]
            )

            partial_match_medley_song_count = 0

            # 完全一致率
            for predicted_item in predicted_items:

                actual_item = actual_by_order.get(
                    predicted_item["song_order"]
                )

                if not actual_item:
                    continue

                predicted_item_songs = predicted_item["songs"]
                actual_item_songs = actual_item["songs"]

                if not predicted_item["is_medley"]:

                    predicted_song = predicted_item_songs[0]
                    actual_song = actual_item_songs[0]

                    if (
                        predicted_song["song_group_id"]
                        == actual_song["song_group_id"]
                    ):
                        match_item_count += 1

                    continue

                predicted_groups = [
                    song["song_group_id"]
                    for song in predicted_item_songs
                ]

                actual_groups = [
                    song["song_group_id"]
                    for song in actual_item_songs
                ]

                if predicted_groups == actual_groups:
                    match_item_count += 1
                    match_medley_count += 1

            # 部分一致率
            actual_groups = [
                song["song_group_id"]
                for item in actual_items
                for song in item["songs"]
            ]

            remaining_actual = actual_groups.copy()

            for item in predicted_items:

                for song in item["songs"]:

                    song_group_id = song["song_group_id"]

                    if song_group_id in remaining_actual:

                        partial_match_song_count += 1

                        if item["is_medley"]:
                            partial_match_medley_song_count += 1

                        remaining_actual.remove(song_group_id)

            if total_item_count == 0:
                match_rate = 0
            else:
                match_rate = round(
                    match_item_count / total_item_count * 100,
                    1
                )

            if total_song_count == 0:
                partial_match_rate = 0
            else:
                partial_match_rate = round(
                    partial_match_song_count / total_song_count * 100,
                    1
                )

            if total_medley_count == 0:
                medley_match_rate = None
            else:
                medley_match_rate = round(
                    match_medley_count / total_medley_count * 100,
                    1
                )

            if total_medley_song_count == 0:
                medley_partial_match_rate = None
            else:
                medley_partial_match_rate = round(
                    partial_match_medley_song_count
                    / total_medley_song_count
                    * 100,
                    1
                )

            return (
                match_rate,
                partial_match_rate,
                medley_match_rate,
                medley_partial_match_rate
            )

    finally:
        conn.close()
