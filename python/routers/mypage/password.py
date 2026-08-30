import re

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from python.models.user import UserModel
from python.core import render, auth
from python.core.security import Security


router = APIRouter()


# =====================================================
# パスワード変更
# =====================================================

@router.get("/password/change")
def password_page(request: Request):
    """パスワード変更画面"""

    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return render(
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
    """パスワード変更"""

    # =====================================================
    # ログイン確認
    # =====================================================

    if not auth.is_login(request):
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    user_id = request.session.get("user_id")

    # =====================================================
    # 入力値整形
    # =====================================================

    old_password = old_password.strip()
    new_password = new_password.strip()
    confirm_password = confirm_password.strip()

    # =====================================================
    # 現在のパスワード入力チェック
    # =====================================================

    if not old_password:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "現在のパスワードが入力されていません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # 新しいパスワード入力チェック
    # =====================================================

    if not new_password:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "新しいパスワードが入力されていません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # 確認用パスワード入力チェック
    # =====================================================

    if not confirm_password:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "確認用のパスワードが入力されていません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # ユーザー取得
    # =====================================================

    user = UserModel.get_user(user_id)

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # =====================================================
    # 現在のパスワード確認
    # =====================================================

    if not Security.verify_password(
            old_password,
            user["password"]
    ):
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "現在のパスワードが違います。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # 新しいパスワードと確認用パスワードの一致確認
    # =====================================================

    if new_password != confirm_password:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "新しいパスワードが一致しません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # 新旧パスワード一致チェック
    # =====================================================

    if Security.verify_password(
            new_password,
            user["password"]
    ):
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "現在と同じパスワードは設定できません。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # パスワード長チェック
    # =====================================================

    if len(new_password) < 8 or len(new_password) > 32:
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "パスワードは8～32文字で入力してください。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # 小文字チェック
    # =====================================================

    if not re.search(r"[a-z]", new_password):
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "小文字を1文字以上含めてください。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # 大文字チェック
    # =====================================================

    if not re.search(r"[A-Z]", new_password):
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "大文字を1文字以上含めてください。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # 数字チェック
    # =====================================================

    if not re.search(r"\d", new_password):
        return render(
            request=request,
            name="templates/mypage/password.html",
            context={
                "message": "数字を1文字以上含めてください。",
                "old_password": old_password,
                "new_password": new_password
            }
        )

    # =====================================================
    # 新しいパスワードをハッシュ化
    # =====================================================

    new_hash = Security.hash_password(
        new_password
    )

    # =====================================================
    # DB更新
    # =====================================================

    UserModel.update_password(
        user_id,
        new_hash
    )

    # =====================================================
    # 完了
    # =====================================================

    return RedirectResponse(
        url="/mypage?password_changed=true",
        status_code=303
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

    # =====================================================
    # ログイン済み確認
    # =====================================================

    if auth.is_login(request):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    # =====================================================
    # トークン未指定
    # =====================================================

    if not token:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワード再設定用のURLが正しくありません。"
            }
        )

    # =====================================================
    # トークン検証
    # =====================================================

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

    # =====================================================
    # ユーザー確認
    # =====================================================

    user = UserModel.get_user(
        data["user_id"]
    )

    if user is None:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワード再設定用のURLが無効です。"
            }
        )

    # =====================================================
    # メールアドレス確認
    # =====================================================

    if user["email"] != data["email"]:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワード再設定用のURLが無効です。"
            }
        )

    # =====================================================
    # 再設定画面表示
    # =====================================================

    return render(
        request=request,
        name="templates/login/password_reset.html",
        context={
            "token": token
        }
    )


@router.post("/password/reset")
def password_reset(
        request: Request,
        token: str = Form(""),
        new_password: str = Form(""),
        confirm_password: str = Form("")
):
    """メールからのパスワード再設定"""

    # =====================================================
    # ログイン済み確認
    # =====================================================

    if auth.is_login(request):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    # =====================================================
    # 入力値整形
    # =====================================================

    token = token.strip()
    new_password = new_password.strip()
    confirm_password = confirm_password.strip()

    # =====================================================
    # トークン確認
    # =====================================================

    if not token:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワード再設定用のURLが正しくありません。"
            }
        )

    # =====================================================
    # トークン検証
    # =====================================================

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

    # =====================================================
    # ユーザー取得
    # =====================================================

    user = UserModel.get_user(
        data["user_id"]
    )

    if user is None:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワード再設定用のURLが無効です。"
            }
        )

    # =====================================================
    # メールアドレス確認
    # =====================================================

    if user["email"] != data["email"]:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワード再設定用のURLが無効です。"
            }
        )

    # =====================================================
    # 新しいパスワード入力チェック
    # =====================================================

    if not new_password:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "新しいパスワードが入力されていません。",
                "token": token
            }
        )

    # =====================================================
    # 確認用パスワード入力チェック
    # =====================================================

    if not confirm_password:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "確認用のパスワードが入力されていません。",
                "token": token
            }
        )

    # =====================================================
    # パスワード一致チェック
    # =====================================================

    if new_password != confirm_password:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "新しいパスワードが一致しません。",
                "token": token
            }
        )

    # =====================================================
    # 現在のパスワードとの一致チェック
    # =====================================================

    if Security.verify_password(
            new_password,
            user["password"]
    ):
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "現在と同じパスワードは設定できません。",
                "token": token
            }
        )

    # =====================================================
    # パスワード長チェック
    # =====================================================

    if len(new_password) < 8 or len(new_password) > 32:
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "パスワードは8～32文字で入力してください。",
                "token": token
            }
        )

    # =====================================================
    # 小文字チェック
    # =====================================================

    if not re.search(r"[a-z]", new_password):
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "小文字を1文字以上含めてください。",
                "token": token
            }
        )

    # =====================================================
    # 大文字チェック
    # =====================================================

    if not re.search(r"[A-Z]", new_password):
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "大文字を1文字以上含めてください。",
                "token": token
            }
        )

    # =====================================================
    # 数字チェック
    # =====================================================

    if not re.search(r"\d", new_password):
        return render(
            request=request,
            name="templates/login/password_reset.html",
            context={
                "message": "数字を1文字以上含めてください。",
                "token": token
            }
        )

    # =====================================================
    # パスワードハッシュ化
    # =====================================================

    new_hash = Security.hash_password(
        new_password
    )

    # =====================================================
    # DB更新
    # =====================================================

    UserModel.update_password(
        data["user_id"],
        new_hash
    )

    # =====================================================
    # 完了
    # =====================================================

    return RedirectResponse(
        url="/login?password_reset=true",
        status_code=303
    )
