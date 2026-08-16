from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.home.oshi import oshi as oshi_model
from python.models.home.oshi import oshi_work as oshi_work_model


router = APIRouter(
    prefix="/home/oshi",
    tags=["home_oshi"]
)


@router.get("")
async def oshi(
        request: Request
):
    oshi_basic = oshi_model.get_oshi_basic()

    return templates.TemplateResponse(
        request=request,
        name="templates/home/oshi/oshi.html",
        context={
            "oshi_basic": oshi_basic
        }
    )


@router.get("/work")
async def oshi_work(
        request: Request
):
    keyword = request.query_params.get(
        "keyword",
        ""
    ).strip()

    sort = request.query_params.get(
        "sort",
        "release_asc"
    )

    valid_sorts = {
        "release_asc",
        "release_desc",
        "name",
        "type"
    }

    if sort not in valid_sorts:
        sort = "release_asc"

    works = oshi_work_model.get_oshi_work_list(
        keyword=keyword,
        sort=sort
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/oshi/work.html",
        context={
            "works": works,
            "keyword": keyword,
            "sort": sort
        }
    )
