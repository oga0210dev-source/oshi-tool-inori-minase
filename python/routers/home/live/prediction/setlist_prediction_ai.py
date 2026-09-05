from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render
from python.core import auth

from python.models.home.live.prediction.setlist_prediction_ai import (
    get_ai_prediction_list,
    get_ai_prediction
)


router = APIRouter(
    prefix="/home/live/prediction/ai",
    tags=["home_live_prediction_ai"]
)


def login_redirect(request: Request):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    return None


@router.get("")
async def ai_setlist_prediction(
    request: Request,
    keyword: str = ""
):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    predictions = get_ai_prediction_list(
        keyword if keyword else None
    )

    return render(
        request=request,
        name="templates/home/live/prediction/ai.html",
        context={
            "predictions": predictions,
            "keyword": keyword
        }
    )


@router.get("/detail/{prediction_id}")
async def ai_setlist_prediction_detail(
    request: Request,
    prediction_id: int
):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    prediction = get_ai_prediction(
        prediction_id
    )

    if not prediction:
        return render(
            request=request,
            name="templates/home/live/prediction/ai.html",
            context={
                "predictions": [],
                "keyword": "",
                "message": "AIセトリ予測が見つかりません。"
            }
        )

    return render(
        request=request,
        name="templates/home/live/prediction/ai_detail.html",
        context={
            "prediction": prediction
        }
    )
