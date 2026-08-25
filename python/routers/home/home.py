from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.models.user import UserModel
from python.core import render
from python.utils.date_utils import calculate_member_period
from python.utils.font import (
    FONT_LIST,
    DEFAULT_FONT_ID
)
from python.models.user_setting import UserSettingModel

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
    return render(
        request=request,
        name="templates/top/top.html"
    )


@router.get("/home")
def home(request: Request):
    user_id = request.session.get("user_id")

    # 現在のフォントID
    if user_id:

        font_id = UserSettingModel.get_font_id(user_id)

    else:

        font_id = request.session.get(
            "font_id",
            DEFAULT_FONT_ID
        )

    if not font_id:
        font_id = DEFAULT_FONT_ID

    # ---------------------------------------------------------
    # 未ログイン
    # ---------------------------------------------------------

    if not user_id:
        return render(
            request=request,
            name="templates/home/home.html",
            context={
                "user": None,
                "member_period": None,
                "is_guest": True,

                "font_list": FONT_LIST,
                "current_font_id": font_id
            }
        )

    # ---------------------------------------------------------
    # ログイン済み
    # ---------------------------------------------------------

    user = UserModel.get_user(user_id)

    member_period = calculate_member_period(
        user["member_since"]
    )

    return render(
        request=request,
        name="templates/home/home.html",
        context={
            "user": user,
            "member_period": member_period,
            "is_guest": False,

            "font_list": FONT_LIST,
            "current_font_id": font_id
        }
    )
