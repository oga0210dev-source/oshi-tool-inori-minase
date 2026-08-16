from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from datetime import date

from python.core import templates
from python.core import auth

from python.models.home.live.archive import archive as archive_model

router = APIRouter(
    prefix="/home/live/archive",
    tags=["home_live_archive"]
)


@router.get("")
async def live_list(
        request: Request
):
    user_id = request.session.get("user_id")

    keyword = request.query_params.get("keyword")
    sort = request.query_params.get("sort", "new")

    lives = archive_model.get_live_archive_list(
        user_id,
        keyword,
        sort
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/archive/archive.html",
        context={
            "lives": lives,
            "today": date.today(),
            "is_login": auth.is_login(request)
        }
    )


@router.post("/attend")
async def attend_live(
        request: Request,
        live_id: int = Form(...)
):
    user_id = request.session.get("user_id")

    archive_model.join_live(
        user_id,
        live_id
    )

    return RedirectResponse(
        "/home/live/archive",
        status_code=303
    )


@router.post("/join")
async def join_live(
        request: Request,
        live_id: int = Form(...)
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session.get("user_id")

    archive_model.join_live(
        user_id,
        live_id
    )

    return RedirectResponse(
        "/home/live/archive",
        status_code=303
    )


@router.post("/cancel")
async def cancel_attend(
        request: Request,
        live_id: int = Form(...)
):
    user_id = request.session.get("user_id")

    archive_model.cancel_join(
        user_id,
        live_id
    )

    return RedirectResponse(
        "/home/live/archive",
        status_code=303
    )
