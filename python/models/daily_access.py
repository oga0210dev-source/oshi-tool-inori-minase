from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from python.core.database import get_connection


JST = ZoneInfo("Asia/Tokyo")

DAILY_ACCESS_THRESHOLDS = [
    10,
    30,
    50,
    100,
    200,
    300,
    500,
    1000,
]


class DailyAccessModel:

    @staticmethod
    def get_access_date() -> str:
        """6:00区切りのアクセス日を取得"""

        now = datetime.now(JST)

        if now.hour < 6:
            now -= timedelta(days=1)

        return now.strftime("%Y-%m-%d")

    @staticmethod
    def record_access(user_id: str) -> dict:
        """当日のアクセスユーザーを記録"""

        access_date = DailyAccessModel.get_access_date()

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO T_DAILY_ACCESS_USER (
                    ACCESS_DATE,
                    USER_ID
                )
                VALUES (
                    %s,
                    %s
                )
                ON CONFLICT (ACCESS_DATE, USER_ID)
                DO NOTHING
                RETURNING USER_ID
            """, (
                access_date,
                user_id
            ))

            result = cursor.fetchone()

            if result:

                cursor.execute("""
                    INSERT INTO T_DAILY_ACCESS (
                        ACCESS_DATE,
                        UNIQUE_USER_COUNT
                    )
                    VALUES (
                        %s,
                        1
                    )
                    ON CONFLICT (ACCESS_DATE)
                    DO UPDATE SET
                        UNIQUE_USER_COUNT =
                            T_DAILY_ACCESS.UNIQUE_USER_COUNT + 1,
                        UPDATED_AT = CURRENT_TIMESTAMP
                    RETURNING UNIQUE_USER_COUNT
                """, (
                    access_date,
                ))

                count_result = cursor.fetchone()

                unique_user_count = (
                    count_result["unique_user_count"]
                    if count_result
                    else 0
                )

            else:

                cursor.execute("""
                    SELECT
                        UNIQUE_USER_COUNT AS unique_user_count
                    FROM T_DAILY_ACCESS
                    WHERE ACCESS_DATE = %s
                """, (
                    access_date,
                ))

                count_result = cursor.fetchone()

                if count_result:

                    unique_user_count = count_result[
                        "unique_user_count"
                    ]

                else:

                    cursor.execute("""
                        SELECT
                            COUNT(*) AS unique_user_count
                        FROM T_DAILY_ACCESS_USER
                        WHERE ACCESS_DATE = %s
                    """, (
                        access_date,
                    ))

                    count_result = cursor.fetchone()

                    unique_user_count = (
                        count_result["unique_user_count"]
                        if count_result
                        else 0
                    )

                    cursor.execute("""
                        INSERT INTO T_DAILY_ACCESS (
                            ACCESS_DATE,
                            UNIQUE_USER_COUNT
                        )
                        VALUES (
                            %s,
                            %s
                        )
                        ON CONFLICT (ACCESS_DATE)
                        DO NOTHING
                    """, (
                        access_date,
                        unique_user_count
                    ))

            conn.commit()

            reached_thresholds = (
                DailyAccessModel.get_reached_thresholds(
                    access_date=access_date,
                    unique_user_count=unique_user_count
                )
            )

            return {
                "access_date": access_date,
                "unique_user_count": unique_user_count,
                "new_access": bool(result),
                "reached_thresholds": reached_thresholds
            }

        finally:
            conn.close()

    @staticmethod
    def get_daily_access_count(access_date: str) -> int:
        """指定日のユニークアクセス数を取得"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) AS unique_user_count
                FROM T_DAILY_ACCESS_USER
                WHERE ACCESS_DATE = %s
            """, (
                access_date,
            ))

            result = cursor.fetchone()

            return (
                result["unique_user_count"]
                if result
                else 0
            )

        finally:
            conn.close()

    @staticmethod
    def save_daily_access_count(access_date: str) -> None:
        """指定日のアクセス数を保存"""

        count = DailyAccessModel.get_daily_access_count(
            access_date
        )

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO T_DAILY_ACCESS (
                    ACCESS_DATE,
                    UNIQUE_USER_COUNT
                )
                VALUES (
                    %s,
                    %s
                )
                ON CONFLICT (ACCESS_DATE)
                DO UPDATE SET
                    UNIQUE_USER_COUNT = EXCLUDED.UNIQUE_USER_COUNT,
                    UPDATED_AT = CURRENT_TIMESTAMP
            """, (
                access_date,
                count
            ))

            conn.commit()

        finally:
            conn.close()

    @staticmethod
    def get_daily_access_list(
            days: int = 7,
            date_from=None,
            date_to=None
    ) -> list[dict]:
        """日別ユニークアクセス数と前日比を取得"""

        access_date = datetime.strptime(
            DailyAccessModel.get_access_date(),
            "%Y-%m-%d"
        ).date()

        if date_to:
            end_date = date_to
        else:
            end_date = access_date

        if date_from:
            start_date = date_from
        else:
            start_date = end_date - timedelta(days=days - 1)

        compare_start_date = start_date - timedelta(days=1)

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    ACCESS_DATE AS access_date,
                    UNIQUE_USER_COUNT AS unique_user_count
                FROM T_DAILY_ACCESS
                WHERE ACCESS_DATE BETWEEN %s AND %s
                ORDER BY ACCESS_DATE DESC
            """, (
                compare_start_date,
                end_date
            ))

            rows = cursor.fetchall()

            access_map = {
                row["access_date"].strftime("%Y-%m-%d"):
                    row["unique_user_count"]
                for row in rows
            }

            result = []

            current_date = end_date

            while current_date >= start_date:
                date_key = current_date.strftime("%Y-%m-%d")

                unique_user_count = access_map.get(
                    date_key,
                    0
                )

                previous_date = current_date - timedelta(days=1)
                previous_date_key = previous_date.strftime("%Y-%m-%d")

                previous_count = access_map.get(
                    previous_date_key
                )

                difference = (
                    unique_user_count - previous_count
                    if previous_count is not None
                    else None
                )

                result.append({
                    "access_date": current_date,
                    "unique_user_count": unique_user_count,
                    "previous_count": previous_count,
                    "difference": difference
                })

                current_date -= timedelta(days=1)

            return result

        finally:
            conn.close()

    @staticmethod
    def get_reached_thresholds(
            access_date: str,
            unique_user_count: int
    ) -> list[int]:
        """通知対象となる未通知の閾値を取得"""

        thresholds = [
            threshold
            for threshold in DAILY_ACCESS_THRESHOLDS
            if threshold <= unique_user_count
        ]

        if not thresholds:
            return []

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    THRESHOLD AS threshold
                FROM T_DAILY_ACCESS_NOTIFICATION
                WHERE ACCESS_DATE = %s
                AND THRESHOLD = ANY(%s)
            """, (
                access_date,
                thresholds
            ))

            notified_thresholds = {
                row["threshold"]
                for row in cursor.fetchall()
            }

            return [
                threshold
                for threshold in thresholds
                if threshold not in notified_thresholds
            ]

        finally:
            conn.close()

    @staticmethod
    def save_notification(
            access_date: str,
            threshold: int
    ) -> None:
        """アクセス数閾値の通知履歴を保存"""

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO T_DAILY_ACCESS_NOTIFICATION (
                    ACCESS_DATE,
                    THRESHOLD
                )
                VALUES (
                    %s,
                    %s
                )
                ON CONFLICT (ACCESS_DATE, THRESHOLD)
                DO NOTHING
            """, (
                access_date,
                threshold
            ))

            conn.commit()

        finally:
            conn.close()
