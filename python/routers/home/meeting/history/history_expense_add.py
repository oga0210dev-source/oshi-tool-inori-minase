from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.home.meeting.history import history_expense_add as history_expense_add_model

router = APIRouter(
    prefix="/home/meeting/history/expense",
    tags=["home_meeting_history_expense"]
)


@router.get("/{meeting_id}")
async def expense_add(
        request: Request,
        meeting_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    expense_types = history_expense_add_model.get_expense_type_list()

    return render(
        request=request,
        name="templates/home/meeting/history/history_expense_add.html",
        context={
            "meeting_id": meeting_id,
            "expense_types": expense_types
        }
    )


@router.post("/{meeting_id}")
async def expense_add_save(
        request: Request,
        meeting_id: int,
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
        meeting_id,
        expense_type_id,
        amount,
        memo
    )

    return RedirectResponse(
        f"/home/meeting/history/detail/{meeting_id}",
        status_code=303
    )
