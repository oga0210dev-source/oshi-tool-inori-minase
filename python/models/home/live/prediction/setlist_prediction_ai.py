from python.core.database import get_connection


def get_ai_prediction_list(keyword=None):
    """
    公開されているAIセトリ予測一覧を取得
    """

    conn = get_connection()

    try:
        sql = """
            SELECT
                p.prediction_id,
                p.live_id,
                l.live_name,
                l.tour_name,
                l.tour_order,
                l.live_date,
                l.venue_id,
                p.prediction_context,
                p.created_at,
                p.updated_at
            FROM t_setlist_prediction_ai p
            INNER JOIN m_live l
                ON p.live_id = l.live_id
            WHERE
                p.is_deleted = FALSE
                AND l.is_deleted = FALSE
        """

        params = []

        if keyword:
            sql += """
                AND (
                    l.live_name ILIKE %s
                    OR l.tour_name ILIKE %s
                )
            """

            keyword_param = f"%{keyword}%"

            params.extend([
                keyword_param,
                keyword_param
            ])

        sql += """
            ORDER BY
                l.live_date DESC,
                l.tour_order DESC,
                l.live_id DESC
        """

        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    finally:
        conn.close()


def get_ai_prediction(prediction_id):
    """
    AIセトリ予測の詳細を取得
    """

    if not prediction_id:
        return None

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # AI予測本体
            cur.execute(
                """
                SELECT
                    p.prediction_id,
                    p.live_id,
                    l.live_name,
                    l.tour_name,
                    l.tour_order,
                    l.live_date,
                    l.venue_id,
                    p.prediction_context,
                    p.created_at,
                    p.updated_at
                FROM t_setlist_prediction_ai p
                INNER JOIN m_live l
                    ON p.live_id = l.live_id
                WHERE
                    p.prediction_id = %s
                    AND p.is_deleted = FALSE
                    AND l.is_deleted = FALSE
                LIMIT 1
                """,
                (prediction_id,)
            )

            prediction = cur.fetchone()

            if not prediction:
                return None

            # AI予測楽曲
            cur.execute(
                """
                SELECT
                    d.prediction_detail_id,
                    d.prediction_id,
                    d.song_id,
                    MIN(s.song_name) AS song_name,
                    MIN(s.album_name) AS album_name,
                    d.predicted_order,
                    d.prediction_score,
                    d.prediction_reason,
                    d.is_required,
                    d.is_medley,
                    d.medley_order,
                    d.created_at,
                    d.updated_at
                FROM t_setlist_prediction_ai_detail d
                LEFT JOIN m_song s
                    ON d.song_id = s.song_group_id
                WHERE
                    d.prediction_id = %s
                GROUP BY
                    d.prediction_detail_id,
                    d.prediction_id,
                    d.song_id,
                    d.predicted_order,
                    d.prediction_score,
                    d.prediction_reason,
                    d.is_required,
                    d.is_medley,
                    d.medley_order,
                    d.created_at,
                    d.updated_at
                ORDER BY
                    d.predicted_order ASC,
                    d.medley_order ASC NULLS LAST
                """,
                (prediction_id,)
            )

            prediction["details"] = cur.fetchall()

            return prediction

    finally:
        conn.close()
