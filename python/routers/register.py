from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from python.models.user import UserModel
from python.core.security import Security
import re

from python.core import templates

router = APIRouter()


@router.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@router.post("/register")
def register_exec(
    request: Request,
    user_id: str = Form(...),
    user_name: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...)
):
    # ユーザID
    if len(user_id) < 4 or len(user_id) > 20:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "ユーザIDは4～20文字で入力してください。"
            }
        )

    if not re.fullmatch(r"[a-zA-Z0-9_]+", user_id):
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "ユーザIDは半角英数字と_のみ使用できます。"
            }
        )

    # 表示名
    if len(user_name) > 20:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "表示名は20文字以内で入力してください。"
            }
        )

    # パスワード
    if len(password) < 8 or len(password) > 32:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "パスワードは8～32文字で入力してください。"
            }
        )

    if not re.search(r"[a-z]", password):
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "小文字を1文字以上含めてください。"
            }
        )

    if not re.search(r"[A-Z]", password):
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "大文字を1文字以上含めてください。"
            }
        )

    if not re.search(r"\d", password):
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "数字を1文字以上含めてください。"
            }
        )

    if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>?/\\|`~]", password):
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "記号を1文字以上含めてください。"
            }
        )

    # パスワード一致
    if password != password_confirm:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "パスワードが一致しません。"
            }
        )

    # 重複チェック
    if UserModel.exists_user_id(user_id):
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "このユーザーIDは既に使用されています。"
            }
        )

    # 登録
    hashed_password = Security.hash_password(password)

    UserModel.create_user(
        user_id,
        user_name,
        hashed_password,
        "USER"
    )

    return {
        "message": "登録が完了しました。"
    }
