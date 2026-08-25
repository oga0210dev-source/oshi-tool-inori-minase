from datetime import date
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.home.meeting import detail as detail_model


router = APIRouter(
    prefix="/home/meeting/detail",
    tags=["home_meeting_detail"]
)


@router.get("/{meeting_id}")
async def meeting_detail(
        request: Request,
        meeting_id: int
):
    user_id = request.session.get("user_id")

    meeting = detail_model.get_meeting_detail(
        user_id,
        meeting_id
    )

    if meeting is None:
        return RedirectResponse(
            "/home/meeting",
            status_code=303
        )

    guests = detail_model.get_meeting_guest_list(
        meeting_id
    )

    today = date.today()

    if meeting["meeting_date"] > today:
        days = (
            meeting["meeting_date"] - today
        ).days

        day_status = f"あと{days}日"

    elif meeting["meeting_date"] < today:
        diff = relativedelta(
            today,
            meeting["meeting_date"]
        )

        total_days = (
            today - meeting["meeting_date"]
        ).days

        day_status = (
            f"{diff.years}年"
            f"{diff.months}ヶ月"
            f"{diff.days}日"
            f"（{total_days}日）経過"
        )

    else:
        day_status = "本日開催"

    performance_type_map = {
        "DAY": "昼公演",
        "NIGHT": "夜公演",
        "PART1": "第1部",
        "PART2": "第2部",
        "PART3": "第3部"
    }

    performance_type = performance_type_map.get(
        meeting["performance_type"],
        meeting["performance_type"]
    )

    return render(
        request=request,
        name="templates/home/meeting/detail.html",
        context={
            "meeting": meeting,
            "guests": guests,
            "today": today,
            "day_status": day_status,
            "performance_type": performance_type,
            "is_login": auth.is_login(request)
        }
    )
