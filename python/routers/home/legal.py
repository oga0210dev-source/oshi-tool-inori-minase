from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from python.core import templates


router = APIRouter(
    prefix="/home/legal",
    tags=["legal"]
)


@router.get("/{legal_type}")
async def legal(
    request: Request,
    legal_type: str
):

    if legal_type not in ["terms", "privacy"]:
        return PlainTextResponse(
            "ページが見つかりません。",
            status_code=404
        )

    return templates.TemplateResponse(
        request=request,
        name=f"templates/commons/legal/{legal_type}.html",
        context={}
    )
