import uuid

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
    # =========================================================
    # ログイン済みの場合
    # =========================================================

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    # =========================================================
    # 未ログインの場合
    # =========================================================

    return render(
        request=request,
        name="templates/top/top.html"
    )


@router.get("/home")
def home(request: Request):
    user_id = request.session.get("user_id")

    # =========================================================
    # Sessionがない場合
    # =========================================================

    if not user_id:

        guest_uuid = request.cookies.get("guest_uuid")

        # -----------------------------------------------------
        # CookieにゲストUUIDがない場合
        # -----------------------------------------------------

        if not guest_uuid:
            return RedirectResponse(
                url="/",
                status_code=303
            )

        # -----------------------------------------------------
        # CookieにゲストUUIDがある場合
        # -----------------------------------------------------

        user = UserModel.get_user_by_guest_uuid(
            guest_uuid
        )

        # -----------------------------------------------------
        # Cookieが不正・削除済みの場合
        # -----------------------------------------------------

        if not user:
            return RedirectResponse(
                url="/",
                status_code=303
            )

        # -----------------------------------------------------
        # 既存ゲストを復元
        # -----------------------------------------------------

        user_id = user["user_id"]

        request.session["user_id"] = user["user_id"]
        request.session["user_name"] = user["user_name"]
        request.session["role"] = user["role"]

        # -----------------------------------------------------
        # フォント
        # -----------------------------------------------------

        font_id = UserSettingModel.get_font_id(user_id)

        if not font_id:
            font_id = DEFAULT_FONT_ID

        # -----------------------------------------------------
        # ホーム表示
        # -----------------------------------------------------

        return render(
            request=request,
            name="templates/home/home.html",
            context={
                "user": user,
                "member_period": None,
                "is_guest": True,

                "font_list": FONT_LIST,
                "current_font_id": font_id
            }
        )

    # =========================================================
    # Sessionがある場合
    # =========================================================

    font_id = UserSettingModel.get_font_id(user_id)

    if not font_id:
        font_id = request.session.get(
            "font_id",
            DEFAULT_FONT_ID
        )

    if not font_id:
        font_id = DEFAULT_FONT_ID

    user = UserModel.get_user(user_id)

    # =========================================================
    # Sessionのユーザーが存在しない場合
    # =========================================================

    if not user:
        request.session.clear()

        return RedirectResponse(
            url="/",
            status_code=303
        )

    # =========================================================
    # ログイン済みユーザーのホーム表示
    # =========================================================

    member_period = calculate_member_period(
        user["member_since"]
    )

    return render(
        request=request,
        name="templates/home/home.html",
        context={
            "user": user,
            "member_period": member_period,
            "is_guest": user["role"] == "guest",

            "font_list": FONT_LIST,
            "current_font_id": font_id
        }
    )
