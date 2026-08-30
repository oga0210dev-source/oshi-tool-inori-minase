from fastapi import (
    APIRouter,
    Request,
    Form
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from python.core.security import Security
from python.core.mail import Mail
from python.core import render, auth
from python.models.user import UserModel


router = APIRouter()


# =========================================================
# メールアドレス変更画面
# =========================================================

@router.get("/email/change", response_class=HTMLResponse)
def change_email(
        request: Request
):
    """メールアドレス変更画面"""

    # -----------------------------------------------------
    # ログイン確認
    # -----------------------------------------------------

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session.get("user_id")

    user = UserModel.get_user(user_id)

    if not user:
        request.session.clear()

        return RedirectResponse(
            "/login",
            status_code=303
        )

    return render(
        request=request,
        name="templates/email/change.html",
        context={
            "user": user
        }
    )


# =========================================================
# メールアドレス変更
# =========================================================

@router.post("/email/change", response_class=HTMLResponse)
def update_email(
        request: Request,
        email: str = Form(...)
):
    """メールアドレス変更処理"""

    # -----------------------------------------------------
    # ログイン確認
    # -----------------------------------------------------

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user_id = request.session.get("user_id")

    # -----------------------------------------------------
    # 現在のユーザー情報取得
    # -----------------------------------------------------

    user = UserModel.get_user(user_id)

    if not user:
        request.session.clear()

        return RedirectResponse(
            "/login",
            status_code=303
        )

    current_email = user["email"]

    # -----------------------------------------------------
    # 入力値整形
    # -----------------------------------------------------

    email = email.strip()

    # -----------------------------------------------------
    # メールアドレス未入力
    # -----------------------------------------------------

    if not email:
        return render(
            request=request,
            name="templates/email/change.html",
            context={
                "user": user,
                "message": "メールアドレスを入力してください。"
            }
        )

    # -----------------------------------------------------
    # 現在のメールアドレスと同じ場合
    # -----------------------------------------------------

    if current_email == email:
        return render(
            request=request,
            name="templates/email/change.html",
            context={
                "user": user,
                "message": "現在登録されているメールアドレスと同じです。"
            }
        )

    # -----------------------------------------------------
    # メールアドレス重複チェック
    # -----------------------------------------------------

    if UserModel.exists_email(
            email=email,
            exclude_user_id=user_id
    ):
        return render(
            request=request,
            name="templates/email/change.html",
            context={
                "user": user,
                "message": "このメールアドレスは既に使用されています。"
            }
        )

    # -----------------------------------------------------
    # メールアドレス更新
    # -----------------------------------------------------

    UserModel.update_email(
        user_id=user_id,
        email=email
    )

    # -----------------------------------------------------
    # 認証トークン生成
    # -----------------------------------------------------

    token = Security.generate_email_verification_token(
        user_id=user_id,
        email=email
    )

    # -----------------------------------------------------
    # 認証URL生成
    # -----------------------------------------------------

    base_url = str(request.base_url).rstrip("/")

    verification_url = (
        f"{base_url}/email/verify"
        f"?token={token}"
    )

    # -----------------------------------------------------
    # 認証メール送信
    # -----------------------------------------------------

    Mail.send(
        to_email=email,
        subject="【推し活オールインワン】メールアドレス認証",
        html=f"""
        <html>
        <body>
            <p>
                推し活オールインワンをご利用いただき
                ありがとうございます。
            </p>

            <p>
                以下のリンクをクリックして、
                メールアドレスの認証を完了してください。
            </p>

            <p>
                <a href="{verification_url}">
                    メールアドレスを認証する
                </a>
            </p>

            <p>
                このリンクの有効期限は24時間です。
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

    # -----------------------------------------------------
    # メール送信後
    # -----------------------------------------------------

    return render(
        request=request,
        name="templates/email/change.html",
        context={
            "user": UserModel.get_user(user_id),
            "email_verification_sent_to": email
        }
    )


# =========================================================
# メールアドレス認証
# =========================================================

@router.get("/email/verify", response_class=HTMLResponse)
def verify_email(
        request: Request,
        token: str = ""
):
    """メールアドレス認証"""

    # =====================================================
    # トークンチェック
    # =====================================================

    if not token:
        return render(
            request=request,
            name="templates/email/verify.html",
            context={
                "success": False,
                "message": "認証URLが正しくありません。"
            }
        )

    # =====================================================
    # トークン検証
    # =====================================================

    data = Security.verify_email_verification_token(
        token
    )

    if not data:
        return render(
            request=request,
            name="templates/email/verify.html",
            context={
                "success": False,
                "message": "認証URLが無効、または有効期限が切れています。"
            }
        )

    user_id = data.get("user_id")
    email = data.get("email")

    if not user_id or not email:
        return render(
            request=request,
            name="templates/email/verify.html",
            context={
                "success": False,
                "message": "認証情報が正しくありません。"
            }
        )

    # =====================================================
    # メールアドレス認証
    # =====================================================

    verified = UserModel.verify_email(
        user_id=user_id,
        email=email
    )

    if not verified:
        return render(
            request=request,
            name="templates/email/verify.html",
            context={
                "success": False,
                "message": "認証に失敗しました。メールアドレスが変更されている可能性があります。"
            }
        )

    # =====================================================
    # 認証成功
    # =====================================================

    return render(
        request=request,
        name="templates/email/verify.html",
        context={
            "success": True,
            "message": "メールアドレスの認証が完了しました。"
        }
    )
