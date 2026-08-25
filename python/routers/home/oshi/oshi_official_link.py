from fastapi import APIRouter, Request

from python.core import render

from python.models.home.oshi import oshi_official_link as oshi_official_link_model


router = APIRouter(
    prefix="/home/oshi/official_link",
    tags=["home_oshi_official_link"]
)


@router.get("")
async def oshi_official_link(
        request: Request
):
    links = (
        oshi_official_link_model.get_oshi_official_link_list()
    )

    return render(
        request=request,
        name="templates/home/oshi/official_link.html",
        context={
            "links": links
        }
    )
