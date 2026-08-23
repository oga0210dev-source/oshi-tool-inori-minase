from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.home.meeting.history import history as history_model


router = APIRouter(
    prefix="/home/meeting/history",
    tags=["home_meeting_history"]
)


@router.get("")
async def meeting_history(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session.get("user_id")

    meetings = history_model.get_meeting_history_list(
        user_id
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/meeting/history/history.html",
        context={
            "meetings": meetings
        }
    )
