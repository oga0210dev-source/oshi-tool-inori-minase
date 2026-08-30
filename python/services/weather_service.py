import json
from datetime import date, timedelta

import requests

from python.core import database
from python.utils.date_utils import to_jst

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# 今日を含めて15日間
FORECAST_DAYS = 15

# JMAモデルを使用する範囲
JMA_FORECAST_DAYS = 10


WEATHER_MAP = {
    0: ("☀️", "晴れ"),
    1: ("🌤️", "晴れ時々曇り"),
    2: ("⛅", "晴れ時々曇り"),
    3: ("☁️", "曇り"),
    45: ("🌫️", "霧"),
    48: ("🌫️", "霧"),
    51: ("🌦️", "弱い霧雨"),
    53: ("🌦️", "霧雨"),
    55: ("🌧️", "強い霧雨"),
    56: ("🌧️", "弱い凍雨"),
    57: ("🌧️", "強い凍雨"),
    61: ("🌧️", "弱い雨"),
    63: ("🌧️", "雨"),
    65: ("🌧️", "強い雨"),
    66: ("🌧️", "弱い凍雨"),
    67: ("🌧️", "強い凍雨"),
    71: ("🌨️", "弱い雪"),
    73: ("🌨️", "雪"),
    75: ("❄️", "強い雪"),
    77: ("🌨️", "雪粒"),
    80: ("🌦️", "弱いにわか雨"),
    81: ("🌧️", "にわか雨"),
    82: ("⛈️", "強いにわか雨"),
    85: ("🌨️", "弱いにわか雪"),
    86: ("❄️", "強いにわか雪"),
    95: ("⛈️", "雷雨"),
    96: ("⛈️", "雷雨・ひょう"),
    99: ("⛈️", "雷雨・ひょう"),
}


def get_forecast_limit():
    """Open-Meteoから取得可能な最終日を返す。"""

    today = date.today()

    return today + timedelta(
        days=FORECAST_DAYS - 1
    )


def _request_weather(
    latitude,
    longitude,
    start_date,
    end_date,
    use_jma=False
):
    """Open-Meteo APIから日別天気予報を取得する。"""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max"
        ]),
        "timezone": "auto",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "cell_selection": "nearest"
    }

    if use_jma:
        params["models"] = "jma_seamless"

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=30
    )

    if not response.ok:
        raise RuntimeError(
            f"天気予報の取得に失敗しました: "
            f"HTTP {response.status_code} / {response.text}"
        )

    data = response.json()

    if data.get("error"):
        raise RuntimeError(
            f"天気予報APIエラー: "
            f"{data.get('reason')}"
        )

    return data


def _convert_daily_weather(data):
    """Open-Meteoのdailyデータを辞書化する。"""

    daily = data.get("daily")

    if not daily or not daily.get("time"):
        return {}

    weather_map = {}

    for index, forecast_date in enumerate(
        daily["time"]
    ):
        current_date = date.fromisoformat(
            forecast_date
        )

        weather_code = daily["weather_code"][index]

        if weather_code is None:
            continue

        icon, weather_name = WEATHER_MAP.get(
            weather_code,
            ("🌤️", "不明")
        )

        weather_map[current_date] = {
            "date": current_date,
            "icon": icon,
            "weather_name": weather_name,
            "temperature_max": (
                daily["temperature_2m_max"][index]
            ),
            "temperature_min": (
                daily["temperature_2m_min"][index]
            ),
            "precipitation_probability": (
                daily[
                    "precipitation_probability_max"
                ][index]
            ),
            "weekday": [
                "月",
                "火",
                "水",
                "木",
                "金",
                "土",
                "日"
            ][current_date.weekday()]
        }

    return weather_map


def get_weather(
    latitude,
    longitude,
    target_date
):
    """
    指定会場・開催日の前日、当日、翌日の
    天気予報を取得する。
    """

    if latitude is None or longitude is None:
        return None

    if isinstance(target_date, str):
        target_date = date.fromisoformat(
            target_date
        )

    today = date.today()
    max_forecast_date = get_forecast_limit()

    # 対象日が予報範囲外
    if (
        target_date < today
        or target_date > max_forecast_date
    ):
        return None

    start_date = max(
        target_date - timedelta(days=1),
        today
    )

    end_date = min(
        target_date + timedelta(days=1),
        max_forecast_date
    )

    days_ahead = (
        target_date - today
    ).days

    # 10日先まではJMA
    use_jma = (
        days_ahead <= JMA_FORECAST_DAYS
    )

    try:

        data = _request_weather(
            latitude,
            longitude,
            start_date,
            end_date,
            use_jma=use_jma
        )

        daily_map = _convert_daily_weather(
            data
        )

    except Exception as e:

        # JMAで失敗した場合は通常モデルへ
        if use_jma:

            print(
                f"[Weather Fallback] "
                f"JMA取得失敗 → 通常モデルへ "
                f"latitude={latitude}, "
                f"longitude={longitude}, "
                f"target_date={target_date}, "
                f"error={e}"
            )

            data = _request_weather(
                latitude,
                longitude,
                start_date,
                end_date,
                use_jma=False
            )

            daily_map = _convert_daily_weather(
                data
            )

        else:
            raise

    weather_list = []

    for offset, label in [
        (-1, "前日"),
        (0, "開催日"),
        (1, "翌日")
    ]:

        forecast_date = (
            target_date
            + timedelta(days=offset)
        )

        weather_data = daily_map.get(
            forecast_date
        )

        if weather_data is None:
            continue

        weather_data = dict(
            weather_data
        )

        weather_data["label"] = label

        weather_list.append(
            weather_data
        )

    if not weather_list:
        return None

    return {
        "weather": weather_list,
        "timezone": data.get("timezone"),
        "updated_at": None
    }


def update_weather_forecast():
    """
    開催予定のライブ・町民集会の天気予報を
    ワークテーブルへ更新する。
    """

    conn = database.get_connection()

    try:

        cursor = conn.cursor()

        today = date.today()

        max_forecast_date = (
            get_forecast_limit()
        )

        print(
            f"[Weather Batch] "
            f"対象期間: "
            f"{today} ～ "
            f"{max_forecast_date}"
        )

        # --------------------------------------------------
        # 対象イベント取得
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT
                l.venue_id,
                l.live_date AS event_date,
                v.latitude,
                v.longitude
            FROM m_live l
            INNER JOIN m_venue v
                ON v.venue_id = l.venue_id
            WHERE l.live_date >= CURRENT_DATE
              AND l.live_date <= %s
              AND l.public_flag = TRUE
              AND l.is_deleted = FALSE
              AND v.public_flag = TRUE
              AND v.is_deleted = FALSE
              AND v.latitude IS NOT NULL
              AND v.longitude IS NOT NULL

            UNION

            SELECT
                m.venue_id,
                m.meeting_date AS event_date,
                v.latitude,
                v.longitude
            FROM m_meeting m
            INNER JOIN m_venue v
                ON v.venue_id = m.venue_id
            WHERE m.meeting_date >= CURRENT_DATE
              AND m.meeting_date <= %s
              AND m.public_flag = TRUE
              AND m.is_deleted = FALSE
              AND v.public_flag = TRUE
              AND v.is_deleted = FALSE
              AND v.latitude IS NOT NULL
              AND v.longitude IS NOT NULL
            """,
            (
                max_forecast_date,
                max_forecast_date
            )
        )

        events = cursor.fetchall()

        print(
            f"[Weather Batch] "
            f"対象イベント数: "
            f"{len(events)}"
        )

        if not events:
            print(
                "天気予報取得対象の開催予定はありません。"
            )
            return

        # --------------------------------------------------
        # ワークテーブルクリア
        # --------------------------------------------------

        cursor.execute(
            """
            DELETE FROM w_weather_forecast
            """
        )

        print(
            "[Weather Batch] "
            "ワークテーブルをクリアしました。"
        )

        # --------------------------------------------------
        # 会場単位でキャッシュ
        # --------------------------------------------------

        venue_map = {}

        for event in events:

            venue_id = event["venue_id"]

            if venue_id not in venue_map:

                venue_map[venue_id] = {
                    "latitude": event["latitude"],
                    "longitude": event["longitude"],
                    "dates": set()
                }

            venue_map[
                venue_id
            ]["dates"].add(
                event["event_date"]
            )

        insert_count = 0

        # --------------------------------------------------
        # 会場ごとに天気取得
        # --------------------------------------------------

        for venue_id, venue in venue_map.items():

            latitude = venue["latitude"]
            longitude = venue["longitude"]

            print(
                f"[Weather Batch] "
                f"venue_id={venue_id}, "
                f"latitude={latitude}, "
                f"longitude={longitude}"
            )

            # 開催日の中で最も早い日・遅い日
            event_dates = sorted(
                venue["dates"]
            )

            start_date = max(
                min(event_dates)
                - timedelta(days=1),
                today
            )

            end_date = min(
                max(event_dates)
                + timedelta(days=1),
                max_forecast_date
            )

            days_ahead = (
                min(event_dates) - today
            ).days

            use_jma = (
                days_ahead <= JMA_FORECAST_DAYS
            )

            try:

                data = _request_weather(
                    latitude,
                    longitude,
                    start_date,
                    end_date,
                    use_jma=use_jma
                )

                daily_map = _convert_daily_weather(
                    data
                )

            except Exception as e:

                if use_jma:

                    print(
                        f"[Weather Fallback] "
                        f"venue_id={venue_id} "
                        f"JMA取得失敗 → "
                        f"通常モデルへ "
                        f"error={e}"
                    )

                    try:

                        data = _request_weather(
                            latitude,
                            longitude,
                            start_date,
                            end_date,
                            use_jma=False
                        )

                        daily_map = (
                            _convert_daily_weather(
                                data
                            )
                        )

                    except Exception as fallback_error:

                        print(
                            f"[Weather Error] "
                            f"venue_id={venue_id}, "
                            f"error={fallback_error}"
                        )

                        continue

                else:

                    print(
                        f"[Weather Error] "
                        f"venue_id={venue_id}, "
                        f"error={e}"
                    )

                    continue

            # --------------------------------------------------
            # 対象日だけワークテーブルへ登録
            # --------------------------------------------------

            for event_date in event_dates:

                for offset in [-1, 0, 1]:

                    forecast_date = (
                        event_date
                        + timedelta(days=offset)
                    )

                    weather_data = daily_map.get(
                        forecast_date
                    )

                    if weather_data is None:
                        print(
                            f"[Weather Skip] "
                            f"天気データなし "
                            f"venue_id={venue_id}, "
                            f"forecast_date={forecast_date}"
                        )
                        continue

                    weather_json = dict(
                        weather_data
                    )

                    weather_json["date"] = (
                        weather_json[
                            "date"
                        ].isoformat()
                    )

                    cursor.execute(
                        """
                        INSERT INTO w_weather_forecast (
                            venue_id,
                            forecast_date,
                            weather
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (
                            venue_id,
                            forecast_date
                        )
                        DO UPDATE SET
                            weather = EXCLUDED.weather,
                            updated_at =
                                CURRENT_TIMESTAMP
                        """,
                        (
                            venue_id,
                            forecast_date,
                            json.dumps(
                                weather_json,
                                ensure_ascii=False
                            )
                        )
                    )

                    insert_count += 1

        conn.commit()

        print(
            f"[Weather Batch] 完了 "
            f"イベント={len(events)}件 / "
            f"会場={len(venue_map)}件 / "
            f"登録={insert_count}件"
        )

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def add_weather_from_work_table(
    events,
    date_key
):
    """ワークテーブルから天気予報を取得してイベントへ追加する。"""

    if not events:
        return events

    conn = database.get_connection()

    try:

        venue_ids = list({
            event["venue_id"]
            for event in events
            if event.get("venue_id") is not None
        })

        if not venue_ids:

            for event in events:
                event["weather"] = None

            return events

        placeholders = ",".join(
            ["%s"] * len(venue_ids)
        )

        with conn.cursor() as cur:

            cur.execute(
                f"""
                SELECT
                    venue_id,
                    forecast_date,
                    weather,
                    updated_at
                FROM w_weather_forecast
                WHERE venue_id IN ({placeholders})
                ORDER BY forecast_date
                """,
                venue_ids
            )

            rows = cur.fetchall()

        weather_map = {
            (
                row["venue_id"],
                row["forecast_date"]
            ): {
                "weather": row["weather"],
                "updated_at": row["updated_at"]
            }
            for row in rows
        }

        for event in events:

            venue_id = event.get(
                "venue_id"
            )

            target_date = event.get(
                date_key
            )

            if (
                venue_id is None
                or target_date is None
            ):
                event["weather"] = None
                continue

            if isinstance(
                target_date,
                str
            ):
                target_date = date.fromisoformat(
                    target_date
                )

            weather_list = []
            updated_at_list = []

            for offset, label in [
                (-1, "前日"),
                (0, "開催日"),
                (1, "翌日")
            ]:

                forecast_date = (
                    target_date
                    + timedelta(days=offset)
                )

                weather_info = weather_map.get(
                    (
                        venue_id,
                        forecast_date
                    )
                )

                if weather_info is None:
                    continue

                weather_data = dict(
                    weather_info["weather"]
                )

                weather_data["label"] = label

                weather_list.append(
                    weather_data
                )

                if weather_info[
                    "updated_at"
                ] is not None:

                    updated_at_list.append(
                        weather_info["updated_at"]
                    )

            if weather_list:

                updated_at = (
                    to_jst(
                        max(updated_at_list)
                    )
                    if updated_at_list
                    else None
                )

                event["weather"] = {
                    "weather": weather_list,
                    "updated_at": updated_at
                }

            else:
                event["weather"] = None

        return events

    finally:
        conn.close()
