import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from python.core import database
from python.models.daily_access import DailyAccessModel
from python.services.discord_service import (
    send_todo_reminder,
    send_daily_access_notification
)
from python.services.inquiry_service import get_active_todos
from python.services.user_cleanup_service import delete_expired_users
from python.services.weather_service import update_weather_forecast
from python.utils.date_utils import get_now

router = APIRouter(
    prefix="/batch",
    tags=["batch"]
)


def check_cron_secret(request: Request):
    cron_secret = os.getenv("CRON_SECRET")

    if cron_secret:
        authorization = request.headers.get("Authorization")

        if authorization != f"Bearer {cron_secret}":
            return JSONResponse(
                status_code=401,
                content={"message": "Unauthorized"}
            )

    return None


@router.get("/todo-reminder")
async def todo_reminder(request: Request):
    unauthorized = check_cron_secret(request)

    if unauthorized:
        return unauthorized

    conn = database.get_connection()

    try:
        todos = get_active_todos(conn)

        if not todos:
            return {
                "success": True,
                "message": "未対応・対応中のToDoはありません。",
                "count": 0
            }

        send_todo_reminder(todos)

        return {
            "success": True,
            "message": "ToDoリマインドを送信しました。",
            "count": len(todos)
        }

    finally:
        conn.close()


@router.get("/weather-forecast")
async def weather_forecast(request: Request):
    unauthorized = check_cron_secret(request)

    if unauthorized:
        return unauthorized

    try:
        update_weather_forecast()

        return {
            "success": True,
            "message": "天気予報を更新しました。"
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"天気予報の更新に失敗しました: {str(e)}"
            }
        )


@router.get("/delete-expired-users")
async def delete_expired_users_batch(request: Request):
    unauthorized = check_cron_secret(request)

    if unauthorized:
        return unauthorized

    try:
        result = delete_expired_users()

        return {
            "success": True,
            "message": "期限切れユーザーを削除しました。",
            "withdrawal_deleted_count": result[
                "withdrawal_deleted_count"
            ],
            "guest_deleted_count": result[
                "guest_deleted_count"
            ]
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": (
                    "期限切れユーザーの削除に失敗しました: "
                    f"{str(e)}"
                )
            }
        )


@router.get("/daily-access")
async def daily_access(request: Request):
    unauthorized = check_cron_secret(request)

    if unauthorized:
        return unauthorized

    try:
        now = get_now()

        # 6:00区切りで現在のアクセス日を取得
        if now.hour < 6:
            current_access_date = now.date() - timedelta(days=1)
        else:
            current_access_date = now.date()

        # 現在のアクセス日の前日を集計
        previous_access_date = current_access_date - timedelta(days=1)

        DailyAccessModel.save_daily_access_count(
            previous_access_date.strftime("%Y-%m-%d")
        )

        count = DailyAccessModel.get_daily_access_count(
            previous_access_date.strftime("%Y-%m-%d")
        )

        send_daily_access_notification(
            access_date=previous_access_date.strftime("%Y-%m-%d"),
            unique_user_count=count
        )

        return {
            "success": True,
            "message": "前日のアクセス数を集計しました。",
            "access_date": str(previous_access_date),
            "unique_user_count": count
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": (
                    "前日のアクセス数の集計に失敗しました: "
                    f"{str(e)}"
                )
            }
        )
