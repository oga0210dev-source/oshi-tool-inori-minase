from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from python.models.user import UserModel
from python.models.user_setting import UserSettingModel
from python.core.security import Security

from python.core import render

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


@router.post("/login")
def login_exec(
        request: Request,
        login_id: str = Form(...),
        password: str = Form(...)
):

    user = UserModel.get_user_by_login_id(login_id)

    if user is None or not Security.verify_password(password, user["password"]):
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
