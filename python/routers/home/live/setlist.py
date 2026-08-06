from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.home.live import setlist as setlist_model


router = APIRouter(
    prefix="/home/live/setlist",
    tags=["home_live_setlist"]
)


@router.get("/{live_id}")
async def live_setlist(
        request: Request,
        live_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    live = setlist_model.get_live_info(
        live_id
    )

    if live is None:
        return RedirectResponse(
            "/home/live/archive",
            status_code=303
        )

    songs = setlist_model.get_setlist(
        live_id
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/setlist.html",
        context={
            "live": live,
            "songs": songs
        }
    )