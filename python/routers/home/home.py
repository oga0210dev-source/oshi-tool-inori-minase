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

    user_id = request.session.get("user_id")

    # 未ログインの場合
    if not user_id:
        return templates.TemplateResponse(
            request=request,
            name="templates/home/home.html",
            context={
                "user": None,
                "member_period": None,
                "is_guest": True
            }
        )

    # ログイン済みの場合
    user = UserModel.get_user(user_id)

    member_period = calculate_member_period(
        user["member_since"]
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/home/home.html",
        context={
            "user": user,
            "member_period": member_period,
            "is_guest": False
        }
    )