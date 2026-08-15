from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.home.oshi import oshi as oshi_model

router = APIRouter(
    prefix="/home/oshi",
    tags=["home_oshi"]
)


@router.get("")
async def oshi(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    oshi_basic = oshi_model.get_oshi_basic()

    return templates.TemplateResponse(
        request=request,
        name="templates/home/oshi/oshi.html",
        context={
            "oshi_basic": oshi_basic
        }
    )
