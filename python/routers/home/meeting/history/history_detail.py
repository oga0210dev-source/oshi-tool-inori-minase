from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.home.meeting.history import history_detail as history_detail_model


router = APIRouter(
    prefix="/home/meeting/history/detail",
    tags=["home_meeting_history_detail"]
)


@router.get("/{meeting_id}")
async def history_detail(
        request: Request,
        meeting_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session.get("user_id")

    meeting = history_detail_model.get_meeting_history_detail(
        user_id,
        meeting_id
    )

    if meeting is None:
        return RedirectResponse(
            "/home/meeting/history",
            status_code=303
        )

    expenses = history_detail_model.get_meeting_expense_list(
        user_id,
        meeting_id
    )

    total_expense = history_detail_model.get_total_expense(
        user_id,
        meeting_id
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/meeting/history/history_detail.html",
        context={
            "meeting": meeting,
            "expenses": expenses,
            "total_expense": total_expense
        }
    )
