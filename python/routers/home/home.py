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

    # =========================================================
    # Sessionがない場合はゲストユーザーを復元・作成
    # =========================================================

    if not user_id:

        guest_uuid = request.cookies.get("guest_uuid")

        # -----------------------------------------------------
        # CookieにゲストUUIDがある場合
        # -----------------------------------------------------

        if guest_uuid:

            user = UserModel.get_user_by_guest_uuid(
                guest_uuid
            )

            # Cookieに対応するゲストが存在する場合
            if user:

                user_id = user["user_id"]

            # Cookieが不正・削除済みの場合
            else:

                guest_uuid = str(uuid.uuid4())
                user_id = guest_uuid

                UserModel.create_guest_user(
                    user_id=user_id,
                    guest_uuid=guest_uuid
                )

                user = UserModel.get_user(user_id)

        # -----------------------------------------------------
        # Cookieがない場合
        # -----------------------------------------------------

        else:

            guest_uuid = str(uuid.uuid4())
            user_id = guest_uuid

            UserModel.create_guest_user(
                user_id=user_id,
                guest_uuid=guest_uuid
            )

            user = UserModel.get_user(user_id)

        # =====================================================
        # Session設定
        # =====================================================

        request.session["user_id"] = user["user_id"]
        request.session["user_name"] = user["user_name"]
        request.session["role"] = user["role"]

        # =====================================================
        # Cookie保存
        # =====================================================

        response = render(
            request=request,
            name="templates/home/home.html",
            context={
                "user": user,
                "member_period": None,
                "is_guest": True,

                "font_list": FONT_LIST,
                "current_font_id": DEFAULT_FONT_ID
            }
        )

        response.set_cookie(
            key="guest_uuid",
            value=guest_uuid,
            max_age=60 * 60 * 24 * 3650,
            httponly=True,
            samesite="lax"
        )

        return response

    # =========================================================
    # ログイン済みユーザー
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

    if not user:
        request.session.clear()

        return RedirectResponse(
            url="/",
            status_code=303
        )

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
