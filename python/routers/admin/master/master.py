from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render, auth
from python.services.weather_service import update_weather_forecast


router = APIRouter()


@router.get("/admin/master")
async def master(request: Request):

    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    return render(
        request=request,
        name="templates/admin/master/master.html",
        context={
            "user_name": request.session.get("user_name"),
            "message": request.query_params.get("message")
        }
    )


@router.post("/admin/master/weather/update")
async def update_weather(request: Request):

    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    try:
        update_weather_forecast()

        return RedirectResponse(
            "/admin/master?message=天気予報を更新しました。",
            status_code=303
        )

    except Exception:
        return RedirectResponse(
            "/admin/master?message=天気予報の更新に失敗しました。",
            status_code=303
        )
