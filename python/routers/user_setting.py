from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.models.user_setting import UserSettingModel


router = APIRouter()


FONT_OPTIONS = {
    "hachi_maru_pop",
    "kiwi_maru",
    "mplus_rounded",
    "noto_sans_jp",
    "yusei_magic",
}


@router.post("/font")
def update_font(
    request: Request,
    font_id: str
):
    if font_id not in FONT_OPTIONS:
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    # Sessionはログイン状態に関係なく更新
    request.session["font_id"] = font_id

    # ログインユーザーの場合はDBにも保存
    user_id = request.session.get("user_id")

    if user_id:
        UserSettingModel.update_font_id(
            user_id,
            font_id
        )

    return RedirectResponse(
        url=request.headers.get("referer", "/home"),
        status_code=303
    )
