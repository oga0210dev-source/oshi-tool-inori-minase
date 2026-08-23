from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import auth
from python.core import templates

from python.models.home.meeting.history import history_edit as history_edit_model

router = APIRouter(
    prefix="/home/meeting/history/edit",
    tags=["home_meeting_history_edit"]
)


@router.get("/{meeting_id}")
async def history_edit(
    request: Request,
    meeting_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session["user_id"]

    record = history_edit_model.get_meeting_record(
        user_id,
        meeting_id
    )

    if record is None:
        record = {
            "seat_info": "",
            "memo": ""
        }

    return templates.TemplateResponse(
        request=request,
        name="templates/home/meeting/history/history_edit.html",
        context={
            "record": record,
            "meeting_id": meeting_id
        }
    )


@router.post("/{meeting_id}")
async def history_edit_save(
    request: Request,
    meeting_id: int,
    seat_info: str = Form(""),
    memo: str = Form("")
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session["user_id"]

    history_edit_model.save_meeting_record(
        user_id,
        meeting_id,
        seat_info,
        memo
    )

    return RedirectResponse(
        f"/home/meeting/history/detail/{meeting_id}",
        status_code=303
    )
