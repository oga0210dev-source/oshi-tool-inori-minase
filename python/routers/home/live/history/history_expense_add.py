from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import auth
from python.core import templates

from python.models.home.live.history import history_expense_add as history_expense_add_model

router = APIRouter(
    prefix="/home/live/history/expense",
    tags=["home_live_history_expense"]
)


@router.get("/{live_id}")
async def expense_add(
        request: Request,
        live_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    expense_types = history_expense_add_model.get_expense_type_list()

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/history/history_expense_add.html",
        context={
            "live_id": live_id,
            "expense_types": expense_types
        }
    )


@router.post("/{live_id}")
async def expense_add_save(
        request: Request,
        live_id: int,
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

    history_expense_add_model.insert_expense(
        user_id,
        live_id,
        expense_type_id,
        amount,
        memo
    )

    return RedirectResponse(
        f"/home/live/history/detail/{live_id}",
        status_code=303
    )
