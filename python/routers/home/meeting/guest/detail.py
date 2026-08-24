from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates

from python.models.home.meeting.guest import detail as detail_model


router = APIRouter(
    prefix="/home/meeting/guest/detail",
    tags=["home_meeting_guest_detail"]
)


@router.get("/{guest_id}")
async def guest_detail(
        request: Request,
        guest_id: int
):
    guest = detail_model.get_guest_detail(
        guest_id
    )

    if guest is None:
        return RedirectResponse(
            "/home/meeting/guest",
            status_code=303
        )

    meetings = detail_model.get_guest_meeting_list(
        guest["guest_name"]
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/meeting/guest/detail.html",
        context={
            "guest": guest,
            "meetings": meetings
        }
    )
