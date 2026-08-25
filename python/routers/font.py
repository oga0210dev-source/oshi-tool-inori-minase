from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from python.core import render
from python.models.user_setting import UserSettingModel
from python.utils.font import (
    FONT_LIST,
    DEFAULT_FONT_ID,
    is_valid_font_id
)

router = APIRouter()


@router.post("/home/font")
def update_font(
        request: Request,
        font_id: str = Form(...)
):
    # 不正なフォントIDを拒否
    if not is_valid_font_id(font_id):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    user_id = request.session.get("user_id")

    # ---------------------------------------------------------
    # ログインユーザー
    # ---------------------------------------------------------

    if user_id:

        UserSettingModel.update_font_id(
            user_id,
            font_id
        )

    # ---------------------------------------------------------
    # 未ログインユーザー
    # ---------------------------------------------------------

    else:

        request.session["font_id"] = font_id

    return RedirectResponse(
        url="/home",
        status_code=303
    )
