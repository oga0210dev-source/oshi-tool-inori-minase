from fastapi import APIRouter, Request

from python.core import render
from python.core import auth

from python.models.home.live import live as live_model
from python.services import weather_service


router = APIRouter(
    prefix="/home/live",
    tags=["home_live"]
)


@router.get("")
async def live_list(
        request: Request
):
    user_id = request.session.get("user_id")
    lives = live_model.get_live_list(user_id)

    weather_service.add_weather_from_work_table(
        lives,
        "live_date"
    )

    return render(
        request=request,
        name="templates/home/live/index.html",
        context={
            "lives": lives,
            "is_login": auth.is_login(request)
        }
    )
