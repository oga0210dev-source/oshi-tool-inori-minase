import requests
from datetime import date, timedelta, timezone
import json

from python.core import database


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
FORECAST_DAYS = 15

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

JST = timezone(timedelta(hours=9))


def to_jst(dt):
    """UTCのdatetimeを日本時間へ変換する。"""
    if dt is None:
        return None

    return dt.replace(tzinfo=timezone.utc).astimezone(JST)


def get_weather(latitude, longitude, target_date):
    if latitude is None or longitude is None:
        return None

    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)

    today = date.today()
    max_forecast_date = today + timedelta(days=FORECAST_DAYS)

    if target_date < today or target_date > max_forecast_date:
        return None

    start_date = max(target_date - timedelta(days=1), today)
    end_date = min(target_date + timedelta(days=1), max_forecast_date)

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
        "end_date": end_date.isoformat()
    }

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
            f"天気予報APIエラー: {data.get('reason')}"
        )

    daily = data.get("daily")

    if not daily or not daily.get("time"):
        return None

    weather_list = []

    for index, forecast_date in enumerate(daily["time"]):
        current_date = date.fromisoformat(forecast_date)

        weather_code = daily["weather_code"][index]

        icon, weather_name = WEATHER_MAP.get(
            weather_code,
            ("🌤️", "不明")
        )

        if current_date == target_date - timedelta(days=1):
            label = "前日"
        elif current_date == target_date:
            label = "開催日"
        elif current_date == target_date + timedelta(days=1):
            label = "翌日"
        else:
            continue

        weather_list.append({
            "date": current_date,
            "label": label,
            "icon": icon,
            "weather_name": weather_name,
            "temperature_max": daily["temperature_2m_max"][index],
            "temperature_min": daily["temperature_2m_min"][index],
            "precipitation_probability": (
                daily["precipitation_probability_max"][index]
            ),
            "weekday": ["月", "火", "水", "木", "金", "土", "日"][
                current_date.weekday()
            ]
        })

    if not weather_list:
        return None

    return {
        "weather": weather_list,
        "timezone": data.get("timezone"),
        "updated_at": None
    }


def update_weather_forecast():
    """開催予定のライブ・町民集会の天気予報をワークテーブルへ更新する。"""

    conn = database.get_connection()

    try:
        cursor = conn.cursor()
        today = date.today()
        max_forecast_date = today + timedelta(days=FORECAST_DAYS)

        print(f"[Weather Batch] 対象期間: {today} ～ {max_forecast_date}")

        cursor.execute("""
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
        """, (
            max_forecast_date,
            max_forecast_date
        ))

        events = cursor.fetchall()

        print(f"[Weather Batch] 対象イベント数: {len(events)}")

        if not events:
            print("天気予報取得対象の開催予定はありません。")
            return

        # 対象がある場合のみワークテーブルをクリア
        cursor.execute("""
            DELETE FROM w_weather_forecast
        """)

        print("[Weather Batch] ワークテーブルをクリアしました。")

        weather_cache = {}

        insert_count = 0

        for event in events:

            venue_id = event["venue_id"]
            event_date = event["event_date"]
            latitude = event["latitude"]
            longitude = event["longitude"]

            print(
                f"[Weather Batch] "
                f"venue_id={venue_id}, "
                f"event_date={event_date}, "
                f"latitude={latitude}, "
                f"longitude={longitude}"
            )

            cache_key = (
                venue_id,
                event_date
            )

            if cache_key not in weather_cache:

                try:
                    weather_cache[cache_key] = get_weather(
                        latitude,
                        longitude,
                        event_date
                    )

                except Exception as e:

                    print(
                        f"[Weather Error] "
                        f"venue_id={venue_id}, "
                        f"event_date={event_date}, "
                        f"error={e}"
                    )

                    weather_cache[cache_key] = None

            weather = weather_cache[cache_key]

            if weather is None:
                print(
                    f"[Weather Skip] "
                    f"天気データなし "
                    f"venue_id={venue_id}, "
                    f"event_date={event_date}"
                )
                continue

            print(
                f"[Weather Batch] "
                f"天気取得成功: "
                f"{len(weather['weather'])}日分"
            )

            for weather_data in weather["weather"]:

                forecast_date = weather_data["date"]

                weather_json = weather_data.copy()
                weather_json["date"] = weather_json["date"].isoformat()

                cursor.execute("""
                    INSERT INTO w_weather_forecast (
                        venue_id,
                        forecast_date,
                        weather
                    )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (venue_id, forecast_date)
                    DO UPDATE SET
                        weather = EXCLUDED.weather,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    venue_id,
                    forecast_date,
                    json.dumps(weather_json, ensure_ascii=False)
                ))

                insert_count += 1

        conn.commit()

        print(
            f"[Weather Batch] 完了 "
            f"イベント={len(events)}件 / "
            f"登録={insert_count}件"
        )

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def add_weather_from_work_table(events, date_key):
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

        placeholders = ",".join(["%s"] * len(venue_ids))

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

        weather_map = {}

        for row in rows:
            weather_map[
                (row["venue_id"], row["forecast_date"])
            ] = {
                "weather": row["weather"],
                "updated_at": row["updated_at"]
            }

        for event in events:

            venue_id = event.get("venue_id")
            target_date = event.get(date_key)

            if venue_id is None or target_date is None:
                event["weather"] = None
                continue

            if isinstance(target_date, str):
                target_date = date.fromisoformat(target_date)

            weather_list = []
            updated_at_list = []

            for offset, label in [
                (-1, "前日"),
                (0, "開催日"),
                (1, "翌日")
            ]:
                forecast_date = target_date + timedelta(days=offset)

                weather_info = weather_map.get(
                    (venue_id, forecast_date)
                )

                if weather_info is None:
                    continue

                weather_data = dict(weather_info["weather"])
                weather_data["label"] = label

                weather_list.append(weather_data)

                if weather_info["updated_at"] is not None:
                    updated_at_list.append(
                        weather_info["updated_at"]
                    )

            if weather_list:

                # 最新の更新日時を取得
                updated_at = (
                    to_jst(max(updated_at_list))
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
