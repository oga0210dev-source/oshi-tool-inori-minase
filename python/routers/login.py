import os
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from python.models.user import UserModel
from python.models.user_setting import UserSettingModel
from python.core.security import Security
from python.core.mail import Mail

from python.core import render, auth

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    return render(
        request=request,
        name="templates/login/login.html"
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# =====================================================
# ログインID忘れ
# =====================================================

@router.get("/login/id-forgot", response_class=HTMLResponse)
def id_forgot_page(request: Request):
    """ログインID忘れ画面"""

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    return render(
        request=request,
        name="templates/login/id_forgot.html"
    )


@router.post("/login/id-forgot", response_class=HTMLResponse)
def id_forgot(
        request: Request,
        email: str = Form(""),
        password: str = Form("")
):
    """ログインID忘れ"""

    # =====================================================
    # ログイン済み確認
    # =====================================================

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    # =====================================================
    # 入力値整形
    # =====================================================

    email = email.strip()

    # =====================================================
    # 入力チェック
    # =====================================================

    if not email:
        return render(
            request=request,
            name="templates/login/id_forgot.html",
            context={
                "message": "メールアドレスを入力してください。",
                "email": email
            }
        )

    if not password:
        return render(
            request=request,
            name="templates/login/id_forgot.html",
            context={
                "message": "パスワードを入力してください。",
                "email": email
            }
        )

    # =====================================================
    # メールアドレスからユーザー取得
    # =====================================================

    user = UserModel.get_user_by_email(email)

    # =====================================================
    # パスワード確認
    # =====================================================

    if user is None or not Security.verify_password(
            password,
            user["password"]
    ):
        return render(
            request=request,
            name="templates/login/id_forgot.html",
            context={
                "message": "メールアドレスまたはパスワードが一致しません。",
                "email": email
            }
        )

    # =====================================================
    # ログインID取得
    # =====================================================

    login_id = user["login_id"]

    # =====================================================
    # ログインID案内メール送信
    # =====================================================

    Mail.send(
        to_email=email,
        subject="【推し活オールインワン】ログインIDのご案内",
        html=f"""
        <html>
        <body>
            <p>
                推し活オールインワンをご利用いただき
                ありがとうございます。
            </p>

            <p>
                ログインIDの確認依頼を受け付けました。
            </p>

            <p>
                お客様のログインIDは以下のとおりです。
            </p>

            <p>
                <strong>{login_id}</strong>
            </p>

            <p>
                このメールに心当たりがない場合は、
                このメールを無視してください。
            </p>

            <hr>

            <p>
                推し活オールインワン
            </p>
        </body>
        </html>
        """
    )

    # =====================================================
    # 完了
    # =====================================================

    return render(
        request=request,
        name="templates/login/id_forgot.html",
        context={
            "message": "ログインIDの案内メールを送信しました。",
            "email": email
        }
    )


@router.get("/login/password-forgot", response_class=HTMLResponse)
def password_forgot_page(request: Request):
    """パスワード忘れ画面"""

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    return render(
        request=request,
        name="templates/login/password_forgot.html"
    )


@router.post("/login/password-forgot", response_class=HTMLResponse)
def password_forgot(
        request: Request,
        login_id: str = Form(""),
        email: str = Form("")
):
    """パスワード忘れ"""

    login_id = login_id.strip()
    email = email.strip()

    # =====================================================
    # 入力チェック
    # =====================================================

    if not login_id:
        return render(
            request=request,
            name="templates/login/password_forgot.html",
            context={
                "message": "ログインIDを入力してください。",
                "login_id": login_id,
                "email": email
            }
        )

    if not email:
        return render(
            request=request,
            name="templates/login/password_forgot.html",
            context={
                "message": "メールアドレスを入力してください。",
                "login_id": login_id,
                "email": email
            }
        )

    # =====================================================
    # ユーザー取得
    # =====================================================

    user = UserModel.get_user_by_login_id(login_id)

    # =====================================================
    # メールアドレス確認
    # =====================================================

    if user is None or user["email"] != email:
        return render(
            request=request,
            name="templates/login/password_forgot.html",
            context={
                "message": "ログインIDまたはメールアドレスが一致しません。",
                "login_id": login_id,
                "email": email
            }
        )

    # =====================================================
    # パスワード再設定トークン生成
    # =====================================================

    token = Security.generate_password_reset_token(
        user_id=user["user_id"],
        email=user["email"]
    )

    # =====================================================
    # パスワード再設定URL
    # =====================================================

    reset_url = (
        f"{os.getenv('BASE_URL')}/password/reset"
        f"?token={token}"
    )

    # =====================================================
    # 再設定メール送信
    # =====================================================

    Mail.send(
        to_email=email,
        subject="【推し活オールインワン】パスワード再設定のご案内",
        html=f"""
        <html>
        <body>

            <p>
                推し活オールインワンをご利用いただきありがとうございます。
            </p>

            <p>
                パスワードの再設定が申請されました。
            </p>

            <p>
                以下のURLからパスワードを再設定してください。
            </p>

            <p>
                <a href="{reset_url}">
                    パスワードを再設定する
                </a>
            </p>

            <p>
                このURLの有効期限は1時間です。
            </p>

            <p>
                このメールに心当たりがない場合は、
                このメールを無視してください。
            </p>

            <hr>

            <p>
                推し活オールインワン
            </p>

        </body>
        </html>
        """
    )

    # =====================================================
    # 完了
    # =====================================================

    return render(
        request=request,
        name="templates/login/password_forgot.html",
        context={
            "message": "パスワード再設定メールを送信しました。",
            "login_id": login_id,
            "email": email
        }
    )


# =====================================================
# パスワード再設定
# =====================================================

@router.get("/password/reset")
def password_reset_page(
        request: Request,
        token: str = ""
):
    """メールからのパスワード再設定画面"""

    # ログイン済みの場合
    if auth.is_login(request):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    # トークン未指定
    if not token:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワード再設定用のURLが正しくありません。"
            }
        )

    # トークン検証
    data = Security.verify_password_reset_token(
        token
    )

    if data is None:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワード再設定用のURLが無効または期限切れです。"
            }
        )

    return render(
        request=request,
        name="templates/login/password_reset.html",
        context={
            "token": token
        }
    )


# =====================================================
# ログイン
# =====================================================

@router.post("/login")
def login_exec(
        request: Request,
        login_id: str = Form(...),
        password: str = Form(...)
):
    user = UserModel.get_user_by_login_id(login_id)

    if user is None or not Security.verify_password(
            password,
            user["password"]
    ):
        return render(
            request=request,
            name="templates/login/login.html",
            context={
                "message": "ログインIDまたはパスワードが一致しません。"
            }
        )

    request.session["user_id"] = user["user_id"]
    request.session["user_name"] = user["user_name"]
    request.session["role"] = user["role"]

    # ========================================
    # フォント設定
    # ========================================

    db_font_id = UserSettingModel.get_font_id(
        user["user_id"]
    )

    session_font_id = request.session.get("font_id")

    if db_font_id:

        # DBに保存済みの設定を優先
        request.session["font_id"] = db_font_id

    elif session_font_id:

        # ログイン前にSessionへ保存していた設定を引き継ぐ
        UserSettingModel.update_font_id(
            user["user_id"],
            session_font_id
        )

        request.session["font_id"] = session_font_id

    else:

        # 未設定の場合はデフォルト
        request.session["font_id"] = "hachi_maru_pop"

        UserSettingModel.update_font_id(
            user["user_id"],
            "hachi_maru_pop"
        )

    return RedirectResponse(
        url="/home",
        status_code=303
    )
