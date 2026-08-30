from datetime import date, datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))


def to_jst(dt):
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(JST)


def calculate_member_period(member_since):
    if not member_since:
        return "未設定"

    # DBが文字列の場合
    if isinstance(member_since, str):
        member_since = datetime.strptime(
            member_since,
            "%Y-%m-%d"
        ).date()

    today = date.today()

    # 総日数
    total_days = (
            today - member_since
    ).days

    # 年
    years = today.year - member_since.year

    # 月日調整
    month = today.month - member_since.month
    day = today.day - member_since.day

    if day < 0:
        month -= 1

        # 前月の日数取得
        if today.month == 1:
            previous_month = date(
                today.year - 1,
                12,
                1
            )
        else:
            previous_month = date(
                today.year,
                today.month - 1,
                1
            )

        days_in_previous_month = (
                date(
                    previous_month.year,
                    previous_month.month + 1,
                    1
                )
                - previous_month
        ).days

        day += days_in_previous_month

    if month < 0:
        years -= 1
        month += 12

    return (
        f"{years}年"
        f"{month}ヶ月"
        f"{day}日"
        f"（{total_days}日）"
    )
