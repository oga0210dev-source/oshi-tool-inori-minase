from fastapi import APIRouter, Request

from python.core import templates

from python.models.home.meeting.guest import guest as guest_model


router = APIRouter(
    prefix="/home/meeting/guest",
    tags=["home_meeting_guest"]
)


@router.get("")
async def guest_list(
        request: Request
):
    guests = guest_model.get_guest_list()

    return templates.TemplateResponse(
        request=request,
        name="templates/home/meeting/guest/index.html",
        context={
            "guests": guests
        }
    )
