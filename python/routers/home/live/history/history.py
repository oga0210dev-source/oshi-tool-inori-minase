from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.home.live.history import history as history_model


router = APIRouter(
    prefix="/home/live/history",
    tags=["home_live_history"]
)


@router.get("")
async def live_history(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session.get("user_id")

    lives = history_model.get_live_history_list(
        user_id
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/history/history.html",
        context={
            "lives": lives
        }
    )
