from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from datetime import date

from python.core import render, auth
from python.models.home.meeting.archive import archive as archive_model

router = APIRouter(
    prefix="/home/meeting/archive",
    tags=["home_meeting_archive"]
)


@router.get("")
async def meeting_list(request: Request):
    user_id = request.session.get("user_id")
    keyword = request.query_params.get("keyword")
    sort = request.query_params.get("sort", "new")

    meetings = archive_model.get_meeting_archive_list(user_id, keyword, sort)

    return render(
        request=request,
        name="templates/home/meeting/archive/archive.html",
        context={
            "meetings": meetings,
            "today": date.today(),
            "is_login": auth.is_login(request)
        }
    )


@router.post("/attend")
async def attend_meeting(request: Request, meeting_id: int = Form(...)):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    user_id = request.session.get("user_id")
    archive_model.join_meeting(user_id, meeting_id)

    return RedirectResponse("/home/meeting/archive", status_code=303)


@router.post("/join")
async def join_meeting(request: Request, meeting_id: int = Form(...)):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    user_id = request.session.get("user_id")
    archive_model.join_meeting(user_id, meeting_id)

    return RedirectResponse("/home/meeting/archive", status_code=303)


@router.post("/cancel")
async def cancel_attend(request: Request, meeting_id: int = Form(...)):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    user_id = request.session.get("user_id")
    archive_model.cancel_join(user_id, meeting_id)

    return RedirectResponse("/home/meeting/archive", status_code=303)
