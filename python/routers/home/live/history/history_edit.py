from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import auth
from python.core import render

from python.models.home.live.history import history_edit as history_edit_model

router = APIRouter(
    prefix="/home/live/history/edit",
    tags=["home_live_history_edit"]
)


@router.get("/{live_id}")
async def history_edit(
    request: Request,
    live_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session["user_id"]

    record = history_edit_model.get_live_record(
        user_id,
        live_id
    )

    if record is None:
        record = {
            "seat_info": "",
            "memo": ""
        }

    return render(
        request=request,
        name="templates/home/live/history/history_edit.html",
        context={
            "record": record,
            "live_id": live_id
        }
    )


@router.post("/{live_id}")
async def history_edit_save(
    request: Request,
    live_id: int,
    seat_info: str = Form(""),
    memo: str = Form("")
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session["user_id"]

    history_edit_model.save_live_record(
        user_id,
        live_id,
        seat_info,
        memo
    )

    return RedirectResponse(
        f"/home/live/history/detail/{live_id}",
        status_code=303
    )
