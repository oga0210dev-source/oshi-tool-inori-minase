from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.home import live as live_model

router = APIRouter(
    prefix="/home/live",
    tags=["home_live"]
)


@router.get("")
async def live_list(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    lives = live_model.get_live_list()

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/index.html",
        context={
            "lives": lives
        }
    )
