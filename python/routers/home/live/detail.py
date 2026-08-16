from datetime import date
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import auth
from python.core import templates

from python.models.home.live import detail as detail_model


router = APIRouter(
    prefix="/home/live/detail",
    tags=["home_live_detail"]
)


@router.get("/{live_id}")
async def live_detail(
        request: Request,
        live_id: int
):
    user_id = request.session.get("user_id")

    live = detail_model.get_live_detail(
        user_id,
        live_id
    )

    if live is None:
        return RedirectResponse(
            "/home/live",
            status_code=303
        )

    today = date.today()

    if live["live_date"] > today:
        days = (live["live_date"] - today).days
        day_status = f"あと{days}日"

    elif live["live_date"] < today:
        diff = relativedelta(
            today,
            live["live_date"]
        )

        total_days = (
            today - live["live_date"]
        ).days

        day_status = (
            f"{diff.years}年"
            f"{diff.months}ヶ月"
            f"{diff.days}日"
            f"（{total_days}日）経過"
        )

    else:
        day_status = "本日開催"

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/detail.html",
        context={
            "live": live,
            "today": today,
            "day_status": day_status,
            "is_login": auth.is_login(request)
        }
    )