from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.home.live import history_detail as history_detail_model


router = APIRouter(
    prefix="/home/live/history/detail",
    tags=["home_live_history_detail"]
)


@router.get("/{live_id}")
async def history_detail(
        request: Request,
        live_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session.get("user_id")

    live = history_detail_model.get_live_history_detail(
        user_id,
        live_id
    )

    if live is None:
        return RedirectResponse(
            "/home/live/history",
            status_code=303
        )

    expenses = history_detail_model.get_live_expense_list(
        user_id,
        live_id
    )

    total_expense = history_detail_model.get_total_expense(
        user_id,
        live_id
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/history_detail.html",
        context={
            "live": live,
            "expenses": expenses,
            "total_expense": total_expense
        }
    )
