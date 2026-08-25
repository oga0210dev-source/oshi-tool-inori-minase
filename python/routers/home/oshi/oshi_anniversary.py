from fastapi import APIRouter, Request

from python.core import render

from python.models.home.oshi import oshi_anniversary as oshi_anniversary_model


router = APIRouter(
    prefix="/home/oshi/anniversary",
    tags=["home_oshi_anniversary"]
)


@router.get("")
async def anniversary(
        request: Request
):
    keyword = request.query_params.get(
        "keyword",
        ""
    ).strip()

    sort = request.query_params.get(
        "sort",
        "next"
    )

    valid_sorts = {
        "next",
        "date_asc",
        "date_desc",
        "name"
    }

    if sort not in valid_sorts:
        sort = "next"

    anniversaries = (
        oshi_anniversary_model.get_anniversary_list(
            keyword=keyword,
            sort=sort
        )
    )

    return render(
        request=request,
        name="templates/home/oshi/anniversary.html",
        context={
            "anniversaries": anniversaries,
            "keyword": keyword,
            "sort": sort
        }
    )
