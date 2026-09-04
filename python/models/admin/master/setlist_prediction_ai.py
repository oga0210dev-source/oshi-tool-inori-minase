from python.core.database import get_connection


def get_live(live_id):
    """
    AIセトリ予測対象のLIVE情報を取得
    管理者用のため、公開状態は問わない。
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    live_id,
                    live_name,
                    tour_name,
                    tour_order,
                    live_date,
                    venue_id,
                    public_flag,
                    is_deleted
                FROM m_live
                WHERE
                    live_id=%s
                    AND is_deleted=FALSE
                """,
                (live_id,)
            )

            return cur.fetchone()
    finally:
        conn.close()


def get_prediction(prediction_id):
    """
    AIセトリ予測を取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
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
                    p.admin_memo,
                    p.public_flag,
                    p.is_deleted,
                    p.created_at,
                    p.updated_at
                FROM t_setlist_prediction_ai p
                INNER JOIN m_live l
                    ON p.live_id=l.live_id
                WHERE
                    p.prediction_id=%s
                    AND p.is_deleted=FALSE
                """,
                (prediction_id,)
            )

            prediction = cur.fetchone()

            if not prediction:
                return None

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
                    ON d.song_id=s.song_group_id
                WHERE
                    d.prediction_id=%s
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


def get_prediction_by_live_id(live_id):
    """
    LIVEに紐づく有効なAIセトリ予測を取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
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
                    p.admin_memo,
                    p.public_flag,
                    p.is_deleted,
                    p.created_at,
                    p.updated_at
                FROM t_setlist_prediction_ai p
                INNER JOIN m_live l
                    ON p.live_id=l.live_id
                WHERE
                    p.live_id=%s
                    AND p.is_deleted=FALSE
                LIMIT 1
                """,
                (live_id,)
            )

            prediction = cur.fetchone()

            if not prediction:
                return None

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
                    ON d.song_id=s.song_group_id
                WHERE
                    d.prediction_id=%s
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
                (
                    prediction[
                        "prediction_id"
                    ],
                )
            )

            prediction["details"] = cur.fetchall()

            return prediction

    finally:
        conn.close()


def get_prediction_list():
    """
    AIセトリ予測一覧を取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.prediction_id,
                    p.live_id,
                    l.live_name,
                    l.tour_name,
                    l.tour_order,
                    l.live_date,
                    p.prediction_context,
                    p.public_flag,
                    p.is_deleted,
                    p.created_at,
                    p.updated_at
                FROM t_setlist_prediction_ai p
                INNER JOIN m_live l
                    ON p.live_id=l.live_id
                WHERE
                    p.is_deleted=FALSE
                ORDER BY
                    l.live_date DESC,
                    l.tour_order ASC,
                    p.prediction_id DESC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()


def create_prediction(
    live_id,
    prediction_context=None,
    admin_memo=None,
    public_flag=False
):
    """
    AIセトリ予測を登録
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO t_setlist_prediction_ai
                (
                    live_id,
                    prediction_context,
                    admin_memo,
                    public_flag
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING prediction_id
                """,
                (
                    live_id,
                    prediction_context,
                    admin_memo,
                    public_flag
                )
            )

            prediction_id = cur.fetchone()["prediction_id"]

        conn.commit()

        return prediction_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def create_prediction_details(
    prediction_id,
    details
):
    """
    AIセトリ予測詳細を登録
    """

    if not prediction_id or not details:
        return

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            for detail in details:
                cur.execute(
                    """
                    INSERT INTO t_setlist_prediction_ai_detail
                    (
                        prediction_id,
                        song_id,
                        predicted_order,
                        prediction_score,
                        prediction_reason,
                        is_required,
                        is_medley,
                        medley_order
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        prediction_id,
                        detail["song_id"],
                        detail["predicted_order"],
                        detail.get("prediction_score"),
                        detail.get("prediction_reason"),
                        detail.get("is_required", False),
                        detail.get("is_medley", False),
                        detail.get("medley_order")
                    )
                )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def update_prediction(
    prediction_id,
    live_id,
    prediction_context=None,
    admin_memo=None,
    public_flag=False
):
    """
    AIセトリ予測を更新
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE t_setlist_prediction_ai
                SET
                    live_id=%s,
                    prediction_context=%s,
                    admin_memo=%s,
                    public_flag=%s,
                    updated_at=CURRENT_TIMESTAMP
                WHERE
                    prediction_id=%s
                    AND is_deleted=FALSE
                """,
                (
                    live_id,
                    prediction_context,
                    admin_memo,
                    public_flag,
                    prediction_id
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def delete_prediction(prediction_id):
    """
    AIセトリ予測を論理削除
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE t_setlist_prediction_ai
                SET
                    is_deleted=TRUE,
                    updated_at=CURRENT_TIMESTAMP
                WHERE
                    prediction_id=%s
                    AND is_deleted=FALSE
                """,
                (prediction_id,)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def delete_prediction_details(prediction_id):
    """
    AIセトリ予測詳細を削除
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM t_setlist_prediction_ai_detail
                WHERE prediction_id=%s
                """,
                (prediction_id,)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def update_prediction_details(
    prediction_id,
    details
):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM t_setlist_prediction_ai_detail
                WHERE prediction_id=%s
                """,
                (prediction_id,)
            )

            for detail in details:
                cur.execute(
                    """
                    INSERT INTO t_setlist_prediction_ai_detail
                    (
                        prediction_id,
                        song_id,
                        predicted_order,
                        prediction_score,
                        prediction_reason,
                        is_required,
                        is_medley,
                        medley_order
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        prediction_id,
                        detail["song_id"],
                        detail["predicted_order"],
                        detail.get("prediction_score"),
                        detail.get("prediction_reason"),
                        detail.get("is_required", False),
                        detail.get("is_medley", False),
                        detail.get("medley_order")
                    )
                )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_live_list():
    """
    AIセトリ予測対象LIVE一覧を取得
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    l.live_id,
                    l.live_name,
                    l.tour_name,
                    l.tour_order,
                    l.live_date,
                    l.venue_id,
                    l.public_flag,
                    l.is_deleted,
                    CASE
                        WHEN p.prediction_id IS NOT NULL
                        THEN TRUE
                        ELSE FALSE
                    END AS has_prediction,
                    p.prediction_id
                FROM m_live l
                LEFT JOIN t_setlist_prediction_ai p
                    ON p.live_id=l.live_id
                    AND p.is_deleted=FALSE
                WHERE
                    l.is_deleted=FALSE
                ORDER BY
                    l.live_date DESC,
                    l.tour_order ASC,
                    l.live_id DESC
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "live_id": row["live_id"],
                    "live_name": row["live_name"],
                    "tour_name": row["tour_name"],
                    "tour_order": row["tour_order"],
                    "live_date": row["live_date"],
                    "venue_id": row["venue_id"],
                    "public_flag": row["public_flag"],
                    "is_deleted": row["is_deleted"],
                    "has_prediction": row["has_prediction"],
                    "prediction_id": row["prediction_id"]
                }
                for row in rows
            ]

    finally:
        conn.close()
