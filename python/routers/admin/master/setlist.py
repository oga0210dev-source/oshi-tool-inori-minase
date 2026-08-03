from fastapi import APIRouter, Request, Form, Body
from fastapi.responses import RedirectResponse

from python.core import templates
from python.models.admin.master import live as live_model, setlist as setlist_model, song as song_model
from python.utils import util

router = APIRouter(
    prefix="/admin/master/setlist/{event_type}/{live_id}",
    tags=["admin_master_setlist"]
)


@router.get("")
async def setlist_list(request: Request, live_id: int):
    live = live_model.get_live(live_id)

    setlist = setlist_model.get_setlist_list(
        event_type="LIVE",
        event_id=live_id
    )

    song_list = song_model.get_song_list()
    album_list = util.group_by_album(song_list)

    return templates.TemplateResponse(
        request,
        "templates/admin/master/setlist/list.html",
        {
            "request": request,
            "live": live,
            "setlist_list": setlist,
            "album_list": album_list
        }
    )


@router.post("/save")
async def save_setlist(
    request: Request,
    event_type: str,
    live_id: int
):
    setlist = await request.json()

    try:
        setlist_model.save_setlist(
            event_type,
            live_id,
            setlist
        )

        return {
            "success": True,
            "message": "セットリストを保存しました。"
        }

    except Exception as e:
        return {
            "success": False,
            "message": "保存に失敗しました。"
        }
