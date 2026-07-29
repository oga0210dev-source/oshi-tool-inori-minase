from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from python.models.user import UserModel
from python.core import templates
from python.core.security import Security
from fastapi import Form
import re

router = APIRouter()


@router.get("/password/change")
def password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="templates/mypage/password.html"
    )


@router.post("/password/change")
def password_change(
        request: Request,
        old_password: str = Form(""),
        new_password: str = Form(""),
        confirm_password: str = Form("")
):
    # 現在のパスワード確認
    user_id = request.session.get("user_id")
    # 未ログイン対策
    if user_id is None:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if not old_password:
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "現在のパスワードが入力されていません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )
    if not new_password:
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "新しいパスワードが入力されていません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )
    if not confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "確認用のパスワードが入力されていません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    user = UserModel.get_user(user_id)

    if not Security.verify_password(
            old_password,
            user["password"]
    ):
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "現在のパスワードが違います。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # 新旧パスワード一致チェック
    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "新しいパスワードが一致しません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # 新旧一致チェック
    if Security.verify_password(
            new_password,
            user["password"]
    ):
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "現在と同じパスワードは設定できません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    if len(new_password) < 8 or len(new_password) > 32:
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "パスワードは8～32文字で入力してください。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    if not re.search(r"[a-z]", new_password):
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "小文字を1文字以上含めてください。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    if not re.search(r"[A-Z]", new_password):
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "大文字を1文字以上含めてください。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    if not re.search(r"\d", new_password):
        return templates.TemplateResponse(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "数字を1文字以上含めてください。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # 新しいパスワードをハッシュ化
    new_hash = Security.hash_password(
        new_password
    )
    # DB更新
    UserModel.update_password(
        user_id,
        new_hash
    )

    return RedirectResponse(
        url="/mypage?password_changed=true",
        status_code=303
    )
