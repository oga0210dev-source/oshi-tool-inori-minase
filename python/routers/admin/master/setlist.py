from fastapi import APIRouter, Request
from python.core import render
from python.models.admin.master import live as live_model, meeting as meeting_model
from python.models.admin.master import setlist as setlist_model, song as song_model

router = APIRouter(
    prefix="/admin/master/setlist/{event_type}/{event_id}",
    tags=["admin_master_setlist"]
)


@router.get("")
async def setlist_list(
        request: Request,
        event_type: str,
        event_id: int
):
    # イベント種別チェック
    if event_type == "LIVE":

        event = live_model.get_live(
            event_id
        )

    elif event_type == "CHOMIN":

        event = meeting_model.get_meeting(
            event_id
        )

    else:
        return {
            "success": False,
            "message": "不正なイベント種別です。"
        }

    # イベントが存在しない場合
    if not event:
        return {
            "success": False,
            "message": "イベントが見つかりません。"
        }

    setlist = setlist_model.get_setlist_list(
        event_type=event_type,
        event_id=event_id
    )

    song_groups = song_model.get_song_groups()

    return render(
        request,
        "templates/admin/master/setlist/list.html",
        {
            "request": request,
            "event_type": event_type,
            "event_id": event_id,
            "event": event,
            "setlist_list": setlist,
            "song_groups": song_groups
        }
    )


@router.post("/save")
async def save_setlist(
        request: Request,
        event_type: str,
        event_id: int
):
    setlist = await request.json()

    try:
        setlist_model.save_setlist(
            event_type,
            event_id,
            setlist
        )

        return {
            "success": True,
            "message": "セットリストを保存しました。"
        }

    except Exception:
        return {
            "success": False,
            "message": "保存に失敗しました。"
        }
