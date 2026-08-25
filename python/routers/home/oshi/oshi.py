from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.home.oshi import oshi as oshi_model

router = APIRouter(
    prefix="/home/oshi",
    tags=["home_oshi"]
)


@router.get("")
async def oshi(
        request: Request
):
    oshi_basic = oshi_model.get_oshi_basic()

    return render(
        request=request,
        name="templates/home/oshi/oshi.html",
        context={
            "oshi_basic": oshi_basic
        }
    )
