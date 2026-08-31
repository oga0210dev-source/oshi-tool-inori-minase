from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render, auth
from python.models.daily_access import DailyAccessModel


router = APIRouter(
    prefix="/admin/master/access",
    tags=["admin_master_access"]
)


@router.get("")
async def access(request: Request):

    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    date_from_text = request.query_params.get("date_from")
    date_to_text = request.query_params.get("date_to")

    date_from = (
        date.fromisoformat(date_from_text)
        if date_from_text
        else None
    )

    date_to = (
        date.fromisoformat(date_to_text)
        if date_to_text
        else None
    )

    access_list = DailyAccessModel.get_daily_access_list(
        date_from=date_from,
        date_to=date_to
    )

    return render(
        request=request,
        name="templates/admin/master/access/index.html",
        context={
            "user_name": request.session.get("user_name"),
            "access_list": access_list
        }
    )
