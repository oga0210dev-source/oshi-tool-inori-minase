import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from python.core import database, auth
from python.services.inquiry_service import get_active_todos
from python.services.discord_service import send_todo_reminder


router = APIRouter(
    prefix="/batch",
    tags=["batch"]
)


@router.get("/todo-reminder")
async def todo_reminder(request: Request):
    cron_secret = os.getenv("CRON_SECRET")

    if cron_secret:
        authorization = request.headers.get("Authorization")

        if authorization != f"Bearer {cron_secret}":
            return JSONResponse(
                status_code=401,
                content={"message": "Unauthorized"}
            )

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
