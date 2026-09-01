import json
from datetime import date, timedelta

import requests

from python.core import database
from python.utils.date_utils import to_jst, get_today


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# 今日を含めて15日間
FORECAST_DAYS = 15

# 開催日が今日から何日先までならJMAモデルを優先するか
JMA_FORECAST_DAYS = 10

# 当日の時間別天気予報の対象時間
HOURLY_START = 9
HOURLY_END = 21


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
    61: ("🌦️", "弱い雨"),
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


# ============================================================
# 共通API
# ============================================================

def _request_open_meteo(
    latitude,
    longitude,
    start_date,
    end_date,
    *,
    daily=False,
    hourly=False,
    use_jma=False
):
    """
    Open-Meteo APIから予報を取得する共通処理。

    JMAモデルでは降水確率が提供されないため、
    JMA取得時には降水確率項目を要求しない。
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "auto",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "cell_selection": "nearest"
    }

    if daily:
        daily_variables = [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min"
        ]

        # 通常モデルでは降水確率を取得
        if not use_jma:
            daily_variables.append(
                "precipitation_probability_max"
            )

        params["daily"] = ",".join(daily_variables)

    if hourly:
        hourly_variables = [
            "weather_code",
            "temperature_2m"
        ]

        # 通常モデルでは降水確率を取得
        if not use_jma:
            hourly_variables.append(
                "precipitation_probability"
            )

        params["hourly"] = ",".join(hourly_variables)

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


# ============================================================
# 日別天気取得
# ============================================================

def _request_weather(
    latitude,
    longitude,
    start_date,
    end_date,
    use_jma=False
):
    """Open-Meteo APIから日別天気予報を取得する。"""

    return _request_open_meteo(
        latitude,
        longitude,
        start_date,
        end_date,
        daily=True,
        use_jma=use_jma
    )


def _convert_daily_weather(data):
    """
    Open-Meteoのdailyデータを辞書化する。

    降水確率はJMAモデルには存在しないため、
    JMAの場合はNoneになる。
    """

    daily = data.get("daily")

    if not daily or not daily.get("time"):
        return {}

    weather_map = {}

    times = daily.get("time", [])
    weather_codes = daily.get("weather_code", [])
    temperature_max = daily.get(
        "temperature_2m_max",
        []
    )
    temperature_min = daily.get(
        "temperature_2m_min",
        []
    )
    precipitation_probability = daily.get(
        "precipitation_probability_max",
        []
    )

    for index, forecast_date in enumerate(times):

        if index >= len(weather_codes):
            continue

        weather_code = weather_codes[index]

        if weather_code is None:
            continue

        current_date = date.fromisoformat(
            forecast_date
        )

        icon, weather_name = WEATHER_MAP.get(
            weather_code,
            ("🌤️", "不明")
        )

        weather_map[current_date] = {
            "date": current_date,
            "icon": icon,
            "weather_name": weather_name,
            "temperature_max": (
                temperature_max[index]
                if index < len(temperature_max)
                else None
            ),
            "temperature_min": (
                temperature_min[index]
                if index < len(temperature_min)
                else None
            ),
            "precipitation_probability": (
                precipitation_probability[index]
                if index < len(
                    precipitation_probability
                )
                else None
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


def _merge_daily_weather(
    jma_map,
    normal_map
):
    """
    JMAを基本データとして使用し、
    不足している降水確率だけ通常モデルから補完する。
    """

    merged_map = {}

    all_dates = set(jma_map.keys()) | set(
        normal_map.keys()
    )

    for forecast_date in all_dates:

        jma_data = jma_map.get(
            forecast_date
        )

        normal_data = normal_map.get(
            forecast_date
        )

        # JMAが存在する場合
        if jma_data is not None:

            merged_data = dict(jma_data)

            # JMAに降水確率がない場合、
            # 通常モデルから補完
            if (
                merged_data.get(
                    "precipitation_probability"
                ) is None
                and normal_data is not None
            ):
                merged_data[
                    "precipitation_probability"
                ] = normal_data.get(
                    "precipitation_probability"
                )

            merged_map[forecast_date] = merged_data

        # JMAがない場合は通常モデル
        elif normal_data is not None:

            merged_map[forecast_date] = dict(
                normal_data
            )

    return merged_map


def _get_daily_weather_by_priority(
    latitude,
    longitude,
    start_date,
    end_date,
    required_dates,
    jma_dates,
    log_prefix=""
):
    """
    日別天気を取得する。

    優先順位：

    1. 天気・気温 → JMA
    2. 降水確率 → 通常モデル
    3. JMA取得失敗 → 通常モデル
    """

    if not required_dates:
        return {}

    jma_map = {}
    normal_map = {}

    # --------------------------------------------------------
    # JMA取得
    # --------------------------------------------------------

    if jma_dates:

        try:
            jma_data = _request_weather(
                latitude,
                longitude,
                start_date,
                end_date,
                use_jma=True
            )

            jma_map = _convert_daily_weather(
                jma_data
            )

            print(
                f"[Weather JMA] "
                f"{log_prefix}"
                f"取得成功 "
                f"dates={sorted(jma_map.keys())}"
            )

        except Exception as e:

            print(
                f"[Weather JMA Error] "
                f"{log_prefix}"
                f"JMA取得失敗 "
                f"error={e}"
            )

    # --------------------------------------------------------
    # 通常モデル取得
    #
    # JMA取得成功時でも、
    # 降水確率補完のため通常モデルを取得する。
    # --------------------------------------------------------

    need_normal = (
        not jma_map
        or any(
            forecast_date not in jma_map
            or jma_map[
                forecast_date
            ].get(
                "precipitation_probability"
            ) is None
            for forecast_date in required_dates
        )
    )

    if need_normal:

        try:
            normal_data = _request_weather(
                latitude,
                longitude,
                start_date,
                end_date,
                use_jma=False
            )

            normal_map = _convert_daily_weather(
                normal_data
            )

            print(
                f"[Weather Normal] "
                f"{log_prefix}"
                f"取得成功 "
                f"dates={sorted(normal_map.keys())}"
            )

        except Exception as e:

            print(
                f"[Weather Normal Error] "
                f"{log_prefix}"
                f"通常モデル取得失敗 "
                f"error={e}"
            )

    # --------------------------------------------------------
    # JMA + 通常モデルをマージ
    # --------------------------------------------------------

    daily_map = _merge_daily_weather(
        jma_map,
        normal_map
    )

    # 必要日だけ返す
    return {
        forecast_date: daily_map[forecast_date]
        for forecast_date in required_dates
        if forecast_date in daily_map
    }


# ============================================================
# 時間別天気
# ============================================================

def _request_hourly_weather(
    latitude,
    longitude,
    target_date,
    use_jma=False
):
    """指定日の時間別天気予報を取得する。"""

    return _request_open_meteo(
        latitude,
        longitude,
        target_date,
        target_date,
        hourly=True,
        use_jma=use_jma
    )


def _convert_hourly_weather(data):
    """時間別天気を9時～21時に絞って辞書化する。"""

    hourly = data.get("hourly")

    if not hourly or not hourly.get("time"):
        return []

    weather_list = []

    times = hourly.get("time", [])
    weather_codes = hourly.get(
        "weather_code",
        []
    )
    temperatures = hourly.get(
        "temperature_2m",
        []
    )
    precipitation_probability = hourly.get(
        "precipitation_probability",
        []
    )

    for index, datetime_value in enumerate(times):

        if index >= len(weather_codes):
            continue

        hour = int(datetime_value[11:13])

        if (
            hour < HOURLY_START
            or hour > HOURLY_END
        ):
            continue

        weather_code = weather_codes[index]

        if weather_code is None:
            continue

        icon, weather_name = WEATHER_MAP.get(
            weather_code,
            ("🌤️", "不明")
        )

        weather_list.append({
            "time": f"{hour:02d}:00",
            "hour": hour,
            "icon": icon,
            "weather_name": weather_name,
            "temperature": (
                temperatures[index]
                if index < len(temperatures)
                else None
            ),
            "precipitation_probability": (
                precipitation_probability[index]
                if index < len(
                    precipitation_probability
                )
                else None
            )
        })

    return weather_list


def _merge_hourly_weather(
    jma_weather,
    normal_weather
):
    """
    JMA時間別天気を基本とし、
    降水確率だけ通常モデルから補完する。
    """

    if not jma_weather:
        return normal_weather

    normal_map = {
        item["hour"]: item
        for item in normal_weather
    }

    merged = []

    for jma_item in jma_weather:

        item = dict(jma_item)

        if (
            item.get(
                "precipitation_probability"
            ) is None
        ):

            normal_item = normal_map.get(
                item["hour"]
            )

            if normal_item is not None:
                item[
                    "precipitation_probability"
                ] = normal_item.get(
                    "precipitation_probability"
                )

        merged.append(item)

    return merged


def _get_hourly_weather(
    latitude,
    longitude,
    target_date,
    log_prefix=""
):
    """
    当日の時間別天気を取得する。

    天気・気温：
        JMA優先

    降水確率：
        通常モデルから補完

    JMA失敗：
        通常モデルへフォールバック
    """

    jma_weather = []
    normal_weather = []

    # --------------------------------------------------------
    # JMA
    # --------------------------------------------------------

    try:

        jma_data = _request_hourly_weather(
            latitude,
            longitude,
            target_date,
            use_jma=True
        )

        jma_weather = _convert_hourly_weather(
            jma_data
        )

        print(
            f"[Weather Hourly JMA] "
            f"{log_prefix}"
            f"取得成功"
        )

    except Exception as e:

        print(
            f"[Weather Hourly JMA Error] "
            f"{log_prefix}"
            f"JMA取得失敗 "
            f"error={e}"
        )

    # --------------------------------------------------------
    # 通常モデル
    #
    # JMAが取得できた場合でも、
    # 降水確率補完のため取得する。
    # --------------------------------------------------------

    need_normal = (
        not jma_weather
        or any(
            item.get(
                "precipitation_probability"
            ) is None
            for item in jma_weather
        )
    )

    if need_normal:

        try:

            normal_data = _request_hourly_weather(
                latitude,
                longitude,
                target_date,
                use_jma=False
            )

            normal_weather = (
                _convert_hourly_weather(
                    normal_data
                )
            )

            print(
                f"[Weather Hourly Normal] "
                f"{log_prefix}"
                f"取得成功"
            )

        except Exception as e:

            print(
                f"[Weather Hourly Normal Error] "
                f"{log_prefix}"
                f"通常モデル取得失敗 "
                f"error={e}"
            )

    # --------------------------------------------------------
    # マージ
    # --------------------------------------------------------

    if jma_weather:

        return _merge_hourly_weather(
            jma_weather,
            normal_weather
        )

    return normal_weather


# ============================================================
# 共通ユーティリティ
# ============================================================

def get_forecast_limit():
    """Open-Meteoから取得可能な最終日を返す。"""

    today = get_today()

    return today + timedelta(
        days=FORECAST_DAYS - 1
    )


def _get_required_forecast_dates(
    event_dates,
    today,
    max_forecast_date
):
    """イベントから実際に必要となる予報日を取得する。"""

    required_dates = set()

    for event_date in event_dates:

        for offset in [-1, 0, 1]:

            forecast_date = (
                event_date
                + timedelta(days=offset)
            )

            if (
                today
                <= forecast_date
                <= max_forecast_date
            ):
                required_dates.add(
                    forecast_date
                )

    return required_dates


# ============================================================
# 公開API
# ============================================================

def get_weather(
    latitude,
    longitude,
    target_date
):
    """
    指定会場・開催日の前日、当日、翌日の
    天気予報を取得する。

    JMA対象期間：
        天気・気温 → JMA
        降水確率 → 通常モデル

    JMA対象外：
        通常モデル

    開催日が当日の場合：
        9:00～21:00の時間別予報を取得する。
    """

    if latitude is None or longitude is None:
        return None

    if isinstance(target_date, str):
        target_date = date.fromisoformat(
            target_date
        )

    today = get_today()
    max_forecast_date = get_forecast_limit()

    if (
        target_date < today
        or target_date > max_forecast_date
    ):
        return None

    required_dates = {
        forecast_date
        for forecast_date in [
            target_date - timedelta(days=1),
            target_date,
            target_date + timedelta(days=1)
        ]
        if (
            today
            <= forecast_date
            <= max_forecast_date
        )
    }

    if not required_dates:
        return None

    start_date = min(required_dates)
    end_date = max(required_dates)

    jma_dates = {
        forecast_date
        for forecast_date in required_dates
        if (
            forecast_date - today
        ).days <= JMA_FORECAST_DAYS
    }

    daily_map = _get_daily_weather_by_priority(
        latitude,
        longitude,
        start_date,
        end_date,
        required_dates,
        jma_dates,
        log_prefix=(
            f"latitude={latitude}, "
            f"longitude={longitude}, "
            f"target_date={target_date}, "
        )
    )

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

    # --------------------------------------------------------
    # 当日の時間別予報
    # --------------------------------------------------------

    hourly_weather = None

    if target_date == today:

        hourly_weather = _get_hourly_weather(
            latitude,
            longitude,
            target_date,
            log_prefix=(
                f"latitude={latitude}, "
                f"longitude={longitude}, "
                f"target_date={target_date}, "
            )
        )

    return {
        "weather": weather_list,
        "hourly_weather": hourly_weather,
        "timezone": None,
        "updated_at": None
    }


# ============================================================
# バッチ更新
# ============================================================

def update_weather_forecast():
    """
    開催予定のライブ・町民集会の天気予報を
    ワークテーブルへ更新する。

    JMA対象期間：
        天気・気温 → JMA
        降水確率 → 通常モデル

    JMA対象外：
        通常モデル
    """

    conn = database.get_connection()

    try:

        cursor = conn.cursor()

        today = get_today()
        max_forecast_date = get_forecast_limit()

        print(
            f"[Weather Batch] "
            f"対象期間: "
            f"{today} ～ "
            f"{max_forecast_date}"
        )

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
            f"対象イベント数: {len(events)}"
        )

        if not events:
            print(
                "天気予報取得対象の開催予定はありません。"
            )
            return

        # ----------------------------------------------------
        # ワークテーブル初期化
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM w_weather_forecast
            """
        )

        print(
            "[Weather Batch] "
            "ワークテーブルをクリアしました。"
        )

        # ----------------------------------------------------
        # 会場単位にまとめる
        # ----------------------------------------------------

        venue_map = {}

        for event in events:

            venue_id = event["venue_id"]

            if venue_id not in venue_map:

                venue_map[venue_id] = {
                    "latitude": event["latitude"],
                    "longitude": event["longitude"],
                    "dates": set()
                }

            venue_map[venue_id]["dates"].add(
                event["event_date"]
            )

        insert_count = 0

        # ----------------------------------------------------
        # 会場ごとに天気取得
        # ----------------------------------------------------

        for venue_id, venue in venue_map.items():

            latitude = venue["latitude"]
            longitude = venue["longitude"]

            event_dates = sorted(
                venue["dates"]
            )

            print(
                f"[Weather Batch] "
                f"venue_id={venue_id}, "
                f"latitude={latitude}, "
                f"longitude={longitude}"
            )

            required_dates = (
                _get_required_forecast_dates(
                    event_dates,
                    today,
                    max_forecast_date
                )
            )

            if not required_dates:
                continue

            start_date = min(
                required_dates
            )

            end_date = max(
                required_dates
            )

            # ------------------------------------------------
            # JMA対象日
            # ------------------------------------------------

            jma_dates = {
                forecast_date
                for forecast_date in required_dates
                if (
                    forecast_date - today
                ).days <= JMA_FORECAST_DAYS
            }

            daily_map = (
                _get_daily_weather_by_priority(
                    latitude,
                    longitude,
                    start_date,
                    end_date,
                    required_dates,
                    jma_dates,
                    log_prefix=(
                        f"venue_id={venue_id}, "
                    )
                )
            )

            # ------------------------------------------------
            # 日別天気を登録
            # ------------------------------------------------

            for event_date in event_dates:

                for offset in [-1, 0, 1]:

                    forecast_date = (
                        event_date
                        + timedelta(days=offset)
                    )

                    if (
                        forecast_date < today
                        or forecast_date > max_forecast_date
                    ):
                        continue

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

            # ------------------------------------------------
            # 当日の時間別天気
            # ------------------------------------------------

            if today in event_dates:

                hourly_weather = (
                    _get_hourly_weather(
                        latitude,
                        longitude,
                        today,
                        log_prefix=(
                            f"venue_id={venue_id}, "
                            f"date={today}, "
                        )
                    )
                )

                if hourly_weather:

                    hourly_json = {
                        "hourly": hourly_weather
                    }

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
                            weather =
                                w_weather_forecast.weather
                                || EXCLUDED.weather,
                            updated_at =
                                CURRENT_TIMESTAMP
                        """,
                        (
                            venue_id,
                            today,
                            json.dumps(
                                hourly_json,
                                ensure_ascii=False
                            )
                        )
                    )

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


# ============================================================
# ワークテーブル → イベントへの付加
# ============================================================

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

        today = get_today()

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
            hourly_weather = None

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

                weather_json = (
                    weather_info["weather"]
                )

                if not isinstance(
                    weather_json,
                    dict
                ):
                    continue

                weather_data = dict(
                    weather_json
                )

                weather_data.pop(
                    "hourly",
                    None
                )

                weather_data["label"] = label

                weather_list.append(
                    weather_data
                )

                if (
                    weather_info["updated_at"]
                    is not None
                ):

                    updated_at_list.append(
                        weather_info[
                            "updated_at"
                        ]
                    )

                # 開催日かつ当日の場合のみ
                # 時間別天気を付加
                if (
                    offset == 0
                    and target_date == today
                ):

                    hourly_weather = (
                        weather_json.get(
                            "hourly"
                        )
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
                    "hourly_weather": (
                        hourly_weather
                    ),
                    "updated_at": updated_at
                }

            else:

                event["weather"] = None

        return events

    finally:

        conn.close()
