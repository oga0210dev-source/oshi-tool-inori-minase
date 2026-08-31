from datetime import date

from fastapi import APIRouter, Request

from python.core import render, auth

from python.models.home.meeting import meeting as meeting_model
from python.services import weather_service


router = APIRouter(
    prefix="/home/meeting",
    tags=["home_meeting"]
)


@router.get("")
async def meeting_list(
        request: Request
):
    user_id = request.session.get("user_id")
    meetings = meeting_model.get_meeting_list(user_id)

    weather_service.add_weather_from_work_table(
        meetings,
        "meeting_date"
    )

    return render(
        request=request,
        name="templates/home/meeting/index.html",
        context={
            "meetings": meetings,
            "is_login": auth.is_login(request),
            "today": date.today()
        }
    )
