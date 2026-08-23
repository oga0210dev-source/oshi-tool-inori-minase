from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import auth

from python.models.home.meeting.history import history_expense_delete as history_expense_delete_model


router = APIRouter(
    prefix="/home/meeting/history/expense/delete",
    tags=["home_meeting_history_expense_delete"]
)


@router.post("/{expense_id}")
async def history_expense_delete(
        request: Request,
        expense_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session["user_id"]

    meeting_id = history_expense_delete_model.get_meeting_id(
        user_id,
        expense_id
    )

    if meeting_id is None:
        return RedirectResponse(
            "/home/meeting/history",
            status_code=303
        )

    history_expense_delete_model.delete_expense(
        user_id,
        expense_id
    )

    return RedirectResponse(
        f"/home/meeting/history/detail/{meeting_id}",
        status_code=303
    )
