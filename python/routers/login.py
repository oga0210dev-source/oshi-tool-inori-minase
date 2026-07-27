from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from python.models.user import UserModel
from python.core.security import Security

from python.core import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login(request: Request):

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/home",
            status_code=303
        )

    return templates.TemplateResponse(
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
        user_id: str = Form(...),
        password: str = Form(...)
):

    user = UserModel.get_user(user_id)

    if user is None or not Security.verify_password(password, user["password"]):
        return templates.TemplateResponse(
            request=request,
            name="templates/login/login.html",
            context={
                "message": "ユーザIDまたはパスワードが一致しません。"
            }
        )

    request.session["user_id"] = user["user_id"]
    request.session["user_name"] = user["user_name"]
    request.session["role"] = user["role"]

    return RedirectResponse(
        url="/home",
        status_code=303
    )
