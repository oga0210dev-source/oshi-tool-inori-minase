from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import auth
from python.core import templates

from python.models.home.live.history import history_expense_add as history_expense_add_model, \
    history_expense_edit as history_expense_edit_model

router = APIRouter(
    prefix="/home/live/history/expense/edit",
    tags=["home_live_history_expense_edit"]
)


@router.get("/{expense_id}")
async def history_expense_edit(
    request: Request,
    expense_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session["user_id"]

    expense = history_expense_edit_model.get_expense(
        user_id,
        expense_id
    )

    if expense is None:
        return RedirectResponse(
            "/home/live/history",
            status_code=303
        )

    expense_types = history_expense_add_model.get_expense_type_list()

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/history/history_expense_edit.html",
        context={
            "expense": expense,
            "expense_types": expense_types
        }
    )


@router.post("/{expense_id}")
async def history_expense_edit_save(
    request: Request,
    expense_id: int,
    expense_type_id: int = Form(...),
    amount: int = Form(...),
    memo: str = Form("")
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session["user_id"]

    live_id = history_expense_edit_model.get_expense(
        user_id,
        expense_id
    )["live_id"]

    history_expense_edit_model.update_expense(
        user_id,
        expense_id,
        expense_type_id,
        memo,
        amount
    )

    return RedirectResponse(
        f"/home/live/history/detail/{live_id}",
        status_code=303
    )
