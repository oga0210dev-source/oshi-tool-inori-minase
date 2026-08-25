from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from python.models.user import UserModel
from python.models.mypage.public_setting import PublicSettingModel
from python.core.security import Security
import re

from python.core import render, auth

router = APIRouter()


@router.get("/register")
def register(request: Request):
    registration_mode = str(auth.get_registration_mode()).strip()

    return render(
        request=request,
        name="templates/register/register.html",
        context={
            "registration_mode": registration_mode
        }
    )


@router.post("/register")
def register_exec(
    request: Request,
    user_id: str = Form(""),
    user_name: str = Form(""),
    password: str = Form(""),
    password_confirm: str = Form(""),
    invitation_code: str = Form("")
):
    registration_mode = auth.get_registration_mode()

    # =========================================================
    # 登録制御
    # =========================================================
    # 登録停止
    if registration_mode == "0":
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "現在、新規ユーザー登録を停止しています。",
                "registration_mode": registration_mode
            }
        )

    # 招待制
    if registration_mode == "2":
        invitation_code = invitation_code.strip()
        if not invitation_code:
            return render(
                request=request,
                name="templates/register/register.html",
                context={
                    "message": "招待コードを入力してください。",
                    "registration_mode": registration_mode,
                    "user_id": user_id, "user_name": user_name
                }
            )
        if not auth.is_valid_invitation_code(invitation_code):
            return render(
                request=request,
                name="templates/register/register.html",
                context={
                    "message": "招待コードが無効です。",
                    "registration_mode": registration_mode,
                    "user_id": user_id,
                    "user_name": user_name
                }

            )

    # =========================================================
    # 必須チェック
    # =========================================================
    if not user_id:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "ユーザIDが入力されていません。",
                "user_id": user_id,
                "user_name": user_name,
                "password": password,
                "registration_mode": registration_mode
            }
        )

    if not user_name:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "ユーザ名が入力されていません。",
                "user_id": user_id,
                "user_name": user_name,
                "password": password,
                "registration_mode": registration_mode
            }
        )

    if not password:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "パスワードが入力されていません。",
                "user_id": user_id,
                "user_name": user_name,
                "password": password,
                "registration_mode": registration_mode
            }
        )

    if not password_confirm:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "確認のパスワードが入力されていません。",
                "user_id": user_id,
                "user_name": user_name,
                "password": password,
                "registration_mode": registration_mode
            }
        )

    # =========================================================
    # ユーザID
    # =========================================================
    if len(user_id) < 4 or len(user_id) > 20:
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "ユーザIDは4～20文字で入力してください。",
                "registration_mode": registration_mode
            }
        )

    if not re.fullmatch(r"[a-zA-Z0-9_]+", user_id):
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "ユーザIDは半角英数字と_のみ使用できます。",
                "registration_mode": registration_mode
            }
        )

    # =========================================================
    # 表示名
    # =========================================================
    if len(user_name) > 20:
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "表示名は20文字以内で入力してください。",
                "registration_mode": registration_mode
            }
        )

    # =========================================================
    # パスワード
    # =========================================================
    if len(password) < 8 or len(password) > 32:
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "パスワードは8～32文字で入力してください。",
                "registration_mode": registration_mode
            }
        )

    if not re.search(r"[a-z]", password):
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "小文字を1文字以上含めてください。",
                "registration_mode": registration_mode
            }
        )

    if not re.search(r"[A-Z]", password):
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "大文字を1文字以上含めてください。",
                "registration_mode": registration_mode
            }
        )

    if not re.search(r"\d", password):
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "数字を1文字以上含めてください。",
                "registration_mode": registration_mode
            }
        )

    # =========================================================
    # パスワード一致
    # =========================================================
    if password != password_confirm:
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "パスワードが一致しません。",
                "registration_mode": registration_mode
            }
        )

    # =========================================================
    # 重複チェック
    # =========================================================
    if UserModel.exists_user_id(user_id):
        return render(
            request=request,
            name="templates/register/register.html",
            context={
                "message": "このユーザーIDは既に使用されています。",
                "registration_mode": registration_mode
            }
        )

    # =========================================================
    # 登録
    # =========================================================
    hashed_password = Security.hash_password(password)

    UserModel.create_user(
        user_id,
        user_name,
        hashed_password
    )

    if registration_mode == "2":
        if not auth.use_invitation_code(invitation_code):
            return render(
                request=request,
                name="templates/register/register.html",
                context={
                    "message": "招待コードの使用に失敗しました。もう一度お試しください。",
                    "registration_mode": registration_mode
                }
            )

    PublicSettingModel.create(user_id)

    # =========================================================
    # セッション保存
    # =========================================================
    request.session["user_id"] = user_id
    request.session["user_name"] = user_name
    request.session["role"] = "user"

    # =========================================================
    # ホームへ
    # =========================================================
    return RedirectResponse(
        url="/home",
        status_code=303
    )
