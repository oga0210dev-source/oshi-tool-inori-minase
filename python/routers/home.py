from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from python.models.user import UserModel
from python.core import templates
from python.utils.date_utils import calculate_member_period

router = APIRouter()


@router.get("/")
def index(request: Request):

    # ログイン済みの場合
    if request.session.get("user_id"):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    # 未ログインの場合
    return templates.TemplateResponse(
        request=request,
        name="templates/top/top.html"
    )


@router.get("/home")
def home(request: Request):

    if not request.session.get("user_id"):
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    user = UserModel.get_user(
        request.session.get("user_id")
    )

    member_period = calculate_member_period(
        user["member_since"]
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/home.html",
        context={
            "user": user,
            "member_period": member_period
        }
    )
