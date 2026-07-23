from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from python.models.user import UserModel
from python.core.security import Security

from python.core import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@router.post("/login")
def login_exec(
        request: Request,
        user_id: str = Form(...),
        password: str = Form(...)
):

    user = UserModel.get_user(user_id)

    if user is None or not Security.verify_password(password, user["PASSWORD"]):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "message": "ユーザIDまたはパスワードが一致しません。"
            }
        )

    request.session["user_id"] = user["USER_ID"]
    request.session["user_name"] = user["USER_NAME"]
    request.session["role"] = user["ROLE"]

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "message": "ログインできました。"
        }
    )
