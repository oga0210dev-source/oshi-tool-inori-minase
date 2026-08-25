from fastapi import Request
from fastapi.templating import Jinja2Templates

from python.models.user_setting import UserSettingModel
from python.utils.font import (
    DEFAULT_FONT_ID,
    get_font_class
)


templates = Jinja2Templates(
    directory="web"
)


def get_font_id(request: Request):

    user_id = request.session.get("user_id")

    # ログインユーザー
    if user_id:

        font_id = UserSettingModel.get_font_id(
            user_id
        )

        if font_id:
            return font_id

    # 未ログインユーザー
    font_id = request.session.get(
        "font_id"
    )

    if font_id:
        return font_id

    return DEFAULT_FONT_ID


def get_font_class_for_request(request: Request):

    font_id = get_font_id(request)

    return get_font_class(font_id)


def render(
    request: Request,
    name: str,
    context: dict | None = None
):

    if context is None:
        context = {}

    # フォントクラスを全ページ共通で渡す
    context["font_class"] = (
        get_font_class_for_request(request)
    )

    # Jinja2Templates本体のTemplateResponseを呼ぶ
    return templates.TemplateResponse(
        request=request,
        name=name,
        context=context
    )
