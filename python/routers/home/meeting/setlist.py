from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.models.home.meeting import setlist as setlist_model


router = APIRouter(
    prefix="/home/meeting/setlist",
    tags=["home_meeting_setlist"]
)


PERFORMANCE_TYPE_LABELS = {
    "DAY": "昼公演",
    "NIGHT": "夜公演",
    "PART1": "第1部",
    "PART2": "第2部",
    "PART3": "第3部"
}


@router.get("/{meeting_id}")
async def meeting_setlist(
        request: Request,
        meeting_id: int
):
    meeting = setlist_model.get_meeting_info(meeting_id)

    if meeting is None:
        return RedirectResponse(
            "/home/meeting/archive",
            status_code=303
        )

    meeting["performance_type_label"] = PERFORMANCE_TYPE_LABELS.get(
        meeting["performance_type"],
        meeting["performance_type"]
    )

    songs = setlist_model.get_setlist(meeting_id)

    return templates.TemplateResponse(
        request=request,
        name="templates/home/meeting/setlist.html",
        context={
            "meeting": meeting,
            "songs": songs
        }
    )
