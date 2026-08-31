from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from python.models.daily_access import DailyAccessModel


JST = ZoneInfo("Asia/Tokyo")


def get_previous_access_date():
    """6:00区切りで前日のアクセス日を取得"""

    now = datetime.now(JST)

    if now.hour < 6:
        current_access_date = now.date() - timedelta(days=1)
    else:
        current_access_date = now.date()

    return current_access_date - timedelta(days=1)


def update_daily_access():
    """前日のアクセス数を確定"""

    access_date = get_previous_access_date()

    DailyAccessModel.save_daily_access_count(
        access_date.strftime("%Y-%m-%d")
    )


if __name__ == "__main__":
    update_daily_access()
