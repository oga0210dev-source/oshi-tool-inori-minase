from python.core.database import get_connection


# ==========================================================
# 共通条件
# ==========================================================

def _get_song_type_condition(mode):
    """
    mode:
        live   : INORIのみ
        chomin : INORIのみ
        all    : 全曲種別
    """

    if mode == "all":
        return ""

    return """
        AND s.song_type = 'INORI'
    """


def _get_event_type_condition(mode):
    """
    mode:
        live   : LIVEのみ
        chomin : LIVE + CHOMIN
        all    : LIVE + CHOMIN
    """

    if mode == "live":
        return """
            st.event_type = 'LIVE'
        """

    return """
        st.event_type IN ('LIVE', 'CHOMIN')
    """


# ==========================================================
# 楽曲回収状況
# ==========================================================

def get_song_collection_summary(user_id, mode="live"):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            song_type_condition = _get_song_type_condition(mode)
            event_type_condition = _get_event_type_condition(mode)

            # --------------------------------------------------
            # マスタ上の総楽曲数
            #
            # song_group_id = 楽曲単位
            # --------------------------------------------------

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

            # --------------------------------------------------
            # ユーザーが参加したイベントで登場した楽曲
            #
            # song_group_id単位で集計
            # --------------------------------------------------

            cur.execute(
                f"""
                SELECT
                    COUNT(DISTINCT s.song_group_id) AS count
                FROM t_live_user u

                INNER JOIN m_live l
                    ON l.live_id = u.live_id

                INNER JOIN m_setlist st
                    ON {event_type_condition}
                    AND st.event_id = l.live_id

                INNER JOIN m_song s
                    ON s.song_id = st.song_id

                WHERE
                    u.user_id = %s
                    AND u.is_join = TRUE

                    AND s.is_public = TRUE
                    AND s.is_deleted = FALSE

                    {song_type_condition}

                    -- 公演中止を除外
                    AND (
                        l.tour_name IS NULL
                        OR l.tour_name NOT LIKE '%%公演中止%%'
                    )
                """,
                (user_id,)
            )

            collected_count = cur.fetchone()["count"]

            # --------------------------------------------------
            # 未回収
            # --------------------------------------------------

            uncollected_count = max(
                total_count - collected_count,
                0
            )

            # --------------------------------------------------
            # 回収率
            # --------------------------------------------------

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


# ==========================================================
# 回収済み楽曲一覧
# ==========================================================

def get_collected_song_list(user_id, mode="live"):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            song_type_condition = _get_song_type_condition(mode)
            event_type_condition = _get_event_type_condition(mode)

            cur.execute(
                f"""
                SELECT
                    s.song_group_id,

                    MIN(s.song_name) AS song_name,

                    MIN(s.youtube_url) AS youtube_url,
                    MIN(s.apple_music_url) AS apple_music_url,
                    MIN(s.spotify_url) AS spotify_url,

                    -- 同一イベント内の重複登録は1回
                    COUNT(
                        DISTINCT
                        st.event_type || ':' || st.event_id
                    ) AS listen_count

                FROM t_live_user u

                INNER JOIN m_live l
                    ON l.live_id = u.live_id

                INNER JOIN m_setlist st
                    ON {event_type_condition}
                    AND st.event_id = l.live_id

                INNER JOIN m_song s
                    ON s.song_id = st.song_id

                WHERE
                    u.user_id = %s
                    AND u.is_join = TRUE

                    AND s.is_public = TRUE
                    AND s.is_deleted = FALSE

                    {song_type_condition}

                    -- 公演中止を除外
                    AND (
                        l.tour_name IS NULL
                        OR l.tour_name NOT LIKE '%%公演中止%%'
                    )

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


# ==========================================================
# 未回収楽曲一覧
# ==========================================================

def get_uncollected_song_list(user_id, mode="live"):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            song_type_condition = _get_song_type_condition(mode)
            event_type_condition = _get_event_type_condition(mode)

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

                        INNER JOIN m_live l
                            ON l.live_id = u.live_id

                        INNER JOIN m_setlist st
                            ON {event_type_condition}
                            AND st.event_id = l.live_id

                        INNER JOIN m_song collected_song
                            ON collected_song.song_id = st.song_id

                        WHERE
                            u.user_id = %s
                            AND u.is_join = TRUE

                            -- ★ song_idではなく
                            --   song_group_idで比較
                            AND collected_song.song_group_id =
                                s.song_group_id

                            -- 公演中止を除外
                            AND (
                                l.tour_name IS NULL
                                OR l.tour_name NOT LIKE '%%公演中止%%'
                            )
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


# ==========================================================
# ライブ登場曲一覧
# ==========================================================

def get_live_appearance_song_list(mode="live"):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            song_type_condition = _get_song_type_condition(mode)
            event_type_condition = _get_event_type_condition(mode)

            cur.execute(
                f"""
                SELECT
                    s.song_group_id,

                    MIN(s.song_name) AS song_name,

                    MIN(s.youtube_url) AS youtube_url,
                    MIN(s.apple_music_url) AS apple_music_url,
                    MIN(s.spotify_url) AS spotify_url,

                    -- 同一イベント内の重複登録は1回
                    COUNT(
                        DISTINCT
                        st.event_type || ':' || st.event_id
                    ) AS appearance_count

                FROM m_setlist st

                INNER JOIN m_song s
                    ON s.song_id = st.song_id

                LEFT JOIN m_live l
                    ON st.event_type = 'LIVE'
                    AND l.live_id = st.event_id

                WHERE
                    {event_type_condition}

                    AND s.is_public = TRUE
                    AND s.is_deleted = FALSE

                    {song_type_condition}

                    -- 公演中止のLIVEは除外
                    AND (
                        st.event_type = 'CHOMIN'
                        OR (
                            l.tour_name IS NULL
                            OR l.tour_name NOT LIKE '%%公演中止%%'
                        )
                    )

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


# ==========================================================
# ライブ登場曲詳細
# ==========================================================

def get_live_appearance_song_detail(
        song_group_id,
        mode="live"
):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            song_type_condition = _get_song_type_condition(mode)
            event_type_condition = _get_event_type_condition(mode)

            # --------------------------------------------------
            # 曲情報
            #
            # song_group_id単位で取得
            # --------------------------------------------------

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
                    s.song_group_id = %s

                    AND s.is_public = TRUE
                    AND s.is_deleted = FALSE

                    {song_type_condition}

                GROUP BY
                    s.song_group_id
                """,
                (song_group_id,)
            )

            song = cur.fetchone()

            if not song:
                return None

            # --------------------------------------------------
            # 登場イベント
            #
            # song_idではなく
            # song_group_id単位で対象曲を判定
            #
            # 同一イベント内で
            # song_id=17
            # song_id=26
            # のように複数バージョンが登録されていても
            # 1イベントとして扱う
            #
            # 公演中止のLIVEは除外
            # --------------------------------------------------

            cur.execute(
                f"""
                WITH distinct_events AS (

                    SELECT DISTINCT
                        st.event_type,
                        st.event_id

                    FROM m_setlist st

                    INNER JOIN m_song s
                        ON s.song_id = st.song_id

                    LEFT JOIN m_live l
                        ON st.event_type = 'LIVE'
                        AND l.live_id = st.event_id

                    LEFT JOIN m_meeting m
                        ON st.event_type = 'CHOMIN'
                        AND m.meeting_id = st.event_id

                    WHERE
                        {event_type_condition}

                        AND s.song_group_id = %s

                        AND s.is_public = TRUE
                        AND s.is_deleted = FALSE

                        {song_type_condition}

                        AND (
                            st.event_type = 'CHOMIN'
                            OR (
                                l.tour_name IS NULL
                                OR l.tour_name NOT LIKE '%%公演中止%%'
                            )
                        )
                )

                SELECT

                    de.event_type,
                    de.event_id,

                    CASE
                        WHEN de.event_type = 'LIVE'
                            THEN l.live_name

                        WHEN de.event_type = 'CHOMIN'
                            THEN m.meeting_name
                    END AS event_name,

                    CASE
                        WHEN de.event_type = 'LIVE'
                            THEN l.live_date

                        WHEN de.event_type = 'CHOMIN'
                            THEN m.meeting_date
                    END AS event_date,

                    v.venue_name

                FROM distinct_events de

                LEFT JOIN m_live l
                    ON de.event_type = 'LIVE'
                    AND l.live_id = de.event_id

                LEFT JOIN m_meeting m
                    ON de.event_type = 'CHOMIN'
                    AND m.meeting_id = de.event_id

                LEFT JOIN m_venue v
                    ON v.venue_id = CASE
                        WHEN de.event_type = 'LIVE'
                            THEN l.venue_id

                        WHEN de.event_type = 'CHOMIN'
                            THEN m.venue_id
                    END

                ORDER BY
                    de.event_type,
                    event_date,
                    de.event_id
                """,
                (song_group_id,)
            )

            events = cur.fetchall()

            return {
                "song_group_id": song["song_group_id"],
                "song_name": song["song_name"],
                "youtube_url": song["youtube_url"],
                "apple_music_url": song["apple_music_url"],
                "spotify_url": song["spotify_url"],
                "events": events
            }

    finally:
        conn.close()
