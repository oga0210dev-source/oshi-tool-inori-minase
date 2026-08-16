from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates, auth

from python.models.home.oshi import oshi_program as program_model


router = APIRouter(
    prefix="/home/oshi/program",
    tags=["home_oshi_program"]
)


@router.get("")
async def program_list(
        request: Request,
        keyword: str = None,
        program_type: str = None,
        sort: str = "display"
):

    programs = program_model.get_program_list(
        keyword,
        program_type,
        sort
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/oshi/program.html",
        context={
            "programs": programs,
            "keyword": keyword,
            "program_type": program_type,
            "sort": sort
        }
    )
