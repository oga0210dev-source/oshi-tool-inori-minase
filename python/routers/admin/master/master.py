from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render, auth

router = APIRouter()


@router.get("/admin/master")
async def master(request: Request):

    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    return render(
        request=request,
        name="templates/admin/master/master.html",
        context={
            "user_name": request.session.get("user_name")
        }
    )
