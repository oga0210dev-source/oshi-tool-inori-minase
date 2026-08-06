from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import auth
from python.models.home.live import history_expense_delete as history_expense_delete_model


router = APIRouter(
    prefix="/home/live/history/expense/delete",
    tags=["home_live_history_expense_delete"]
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

    live_id = history_expense_delete_model.get_live_id(
        user_id,
        expense_id
    )

    if live_id is None:
        return RedirectResponse(
            "/home/live/history",
            status_code=303
        )

    history_expense_delete_model.delete_expense(
        user_id,
        expense_id
    )

    return RedirectResponse(
        f"/home/live/history/detail/{live_id}",
        status_code=303
    )
