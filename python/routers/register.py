from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.models.user import UserModel
from python.models.mypage.public_setting import PublicSettingModel
from python.core.security import Security
from python.core import render

import re


router = APIRouter()


# =========================================================
# 共通：登録画面表示
# =========================================================

def render_register(
        request: Request,
        is_guest_registration: bool = False,
        user_id: str = "",
        user_name: str = "",
        message: str = None
):
    return render(
        request=request,
        name="templates/register/register.html",
        context={
            "is_guest_registration": is_guest_registration,
            "user_id": user_id,
            "user_name": user_name,
            "message": message
        }
    )


# =========================================================
# 新規登録 / ゲスト本登録
# =========================================================

@router.get("/register")
def register(request: Request):

    session_user_id = request.session.get("user_id")
    session_role = request.session.get("role")

    # =====================================================
    # ゲストユーザーの場合
    # =====================================================

    if session_user_id and session_role == "guest":

        user = UserModel.get_user(session_user_id)

        if not user:
            request.session.clear()

            return RedirectResponse(
                url="/",
                status_code=303
            )

        return render_register(
            request=request,
            is_guest_registration=True,
            user_id="",
            user_name=""
        )

    # =====================================================
    # 通常ユーザーがアクセスした場合
    # =====================================================

    if session_user_id and session_role == "user":
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    # =====================================================
    # 未ログイン → 通常の新規登録
    # =====================================================

    return render_register(
        request=request,
        is_guest_registration=False
    )


# =========================================================
# 登録処理
# =========================================================

@router.post("/register")
def register_exec(
    request: Request,
    user_id: str = Form(""),
    user_name: str = Form(""),
    password: str = Form(""),
    password_confirm: str = Form("")
):

    # =====================================================
    # 入力値整形
    # =====================================================

    user_id = user_id.strip()
    user_name = user_name.strip()

    # =====================================================
    # セッション確認
    # =====================================================

    session_user_id = request.session.get("user_id")
    session_role = request.session.get("role")

    is_guest_registration = (
        session_user_id is not None
        and session_role == "guest"
    )

    # =====================================================
    # ゲスト本登録の場合
    # =====================================================

    guest_user_id = None

    if is_guest_registration:

        guest_user_id = session_user_id

        guest_user = UserModel.get_user(guest_user_id)

        if not guest_user:
            request.session.clear()

            return RedirectResponse(
                url="/",
                status_code=303
            )

        # 念のためDB側でもguestであることを確認
        if guest_user["role"] != "guest":
            return RedirectResponse(
                url="/home",
                status_code=303
            )

    # =====================================================
    # 通常ユーザー登録の場合
    # =====================================================

    else:

        # ログイン済み通常ユーザーなら登録不可
        if session_user_id and session_role == "user":
            return RedirectResponse(
                url="/home",
                status_code=303
            )

    # =====================================================
    # 必須チェック
    # =====================================================

    if not user_id:
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="ユーザIDが入力されていません。"
        )

    if not user_name:
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="表示名が入力されていません。"
        )

    if not password:
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="パスワードが入力されていません。"
        )

    if not password_confirm:
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="確認のパスワードが入力されていません。"
        )

    # =====================================================
    # ユーザIDチェック
    # =====================================================

    if len(user_id) < 4 or len(user_id) > 20:
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="ユーザIDは4～20文字で入力してください。"
        )

    if not re.fullmatch(r"[a-zA-Z0-9_]+", user_id):
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="ユーザIDは半角英数字と_のみ使用できます。"
        )

    # =====================================================
    # 表示名チェック
    # =====================================================

    if len(user_name) > 20:
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="表示名は20文字以内で入力してください。"
        )

    # =====================================================
    # パスワードチェック
    # =====================================================

    if len(password) < 8 or len(password) > 32:
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="パスワードは8～32文字で入力してください。"
        )

    if not re.search(r"[a-z]", password):
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="小文字を1文字以上含めてください。"
        )

    if not re.search(r"[A-Z]", password):
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="大文字を1文字以上含めてください。"
        )

    if not re.search(r"\d", password):
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="数字を1文字以上含めてください。"
        )

    # =====================================================
    # パスワード一致
    # =====================================================

    if password != password_confirm:
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="パスワードが一致しません。"
        )

    # =====================================================
    # ユーザID重複チェック
    # =====================================================

    # 本登録の場合は、
    # 「現在のゲストユーザー自身のUSER_ID」と
    # 「新しく入力したUSER_ID」が別物なので、
    # 通常のexists_user_idをそのまま使う。
    #
    # ただし、ゲストユーザーのUSER_IDと同じIDを
    # 本登録用IDとして入力することも禁止する。

    if UserModel.exists_user_id(user_id):
        return render_register(
            request=request,
            is_guest_registration=is_guest_registration,
            user_id=user_id,
            user_name=user_name,
            message="このユーザーIDは既に使用されています。"
        )

    # =====================================================
    # パスワードハッシュ化
    # =====================================================

    hashed_password = Security.hash_password(password)

    # =====================================================
    # ユーザー登録
    # =====================================================

    if is_guest_registration:

        # ---------------------------------------------
        # ゲスト → 本登録
        # ---------------------------------------------

        UserModel.convert_guest_to_user(
            user_id=guest_user_id,
            login_id=user_id,
            user_name=user_name,
            password=hashed_password
        )

        # ゲスト時のセッションユーザーIDは、
        # 本登録後も内部USER_IDとしてそのまま使用する
        request.session["user_id"] = guest_user_id

    else:

        # ---------------------------------------------
        # 完全な新規登録
        # ---------------------------------------------

        UserModel.create_user(
            user_id=user_id,
            user_name=user_name,
            password=hashed_password
        )

        PublicSettingModel.create(user_id)

        request.session["user_id"] = user_id

    # =====================================================
    # セッション更新
    # =====================================================

    request.session["user_name"] = user_name
    request.session["role"] = "user"

    # =====================================================
    # ホームへ
    # =====================================================

    return RedirectResponse(
        url="/home",
        status_code=303
    )
