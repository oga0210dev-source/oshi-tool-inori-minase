from python.core.database import get_connection
from python.utils.date_utils import get_today


def get_live_list(user_id):
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
                    l.venue_id,
                    v.venue_name,
                    v.latitude,
                    v.longitude,
                    p.prefecture_name,
                    COALESCE(u.is_join, FALSE) AS is_join,
                    CASE
                        WHEN COUNT(w.forecast_id) > 0 THEN
                            jsonb_build_object(
                                'weather',
                                jsonb_agg(
                                    w.weather
                                    ORDER BY w.forecast_date
                                )
                            )
                        ELSE NULL
                    END AS weather
                FROM m_live l
                LEFT JOIN m_venue v
                    ON l.venue_id = v.venue_id
                LEFT JOIN m_prefecture p
                    ON v.prefecture_code = p.prefecture_code
                LEFT JOIN t_live_user u
                    ON l.live_id = u.live_id
                   AND u.user_id = %s
                LEFT JOIN w_weather_forecast w
                    ON v.venue_id = w.venue_id
                   AND w.forecast_date BETWEEN
                       l.live_date - INTERVAL '1 day'
                       AND l.live_date + INTERVAL '1 day'
                WHERE
                    l.is_deleted = FALSE
                    AND l.public_flag = TRUE
                    AND l.live_date >= CURRENT_DATE
                GROUP BY
                    l.live_id,
                    l.live_name,
                    l.tour_name,
                    l.live_date,
                    v.venue_name,
                    v.latitude,
                    v.longitude,
                    p.prefecture_name,
                    u.is_join
                ORDER BY
                    l.live_date ASC
                """,
                (user_id,)
            )

            lives = cur.fetchall()

            for live in lives:
                live["remaining_days"] = (
                    live["live_date"] - get_today()
                ).days

            return lives

    finally:
        conn.close()
