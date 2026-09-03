from fastapi import APIRouter, Request
from python.core import render
from python.models.admin.master import announcement as announcement_model

router = APIRouter(
    prefix="/home/announcement",
    tags=["home_announcement"]
)


@router.get("")
async def announcement_list(request: Request):
    announcements = announcement_model.get_public_announcement_list()

    return render(
        request=request,
        name="templates/home/announcement/index.html",
        context={
            "announcements": announcements
        }
    )
