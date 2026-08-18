from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.admin.system import registration as registration_model


router = APIRouter(
    prefix="/admin/system/registration",
    tags=["admin_system_registration"]
)


@router.get("")
async def registration_page(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    registration_mode = registration_model.get_registration_mode()

    message = request.session.pop("message", None)

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/system/registration/form.html",
        context={
            "registration_mode": registration_mode,
            "message": message
        }
    )


@router.post("")
async def registration_update(
        request: Request,
        registration_mode: str = Form(...)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    if registration_mode not in ("0", "1", "2"):
        return RedirectResponse(
            "/admin/system/registration",
            status_code=303
        )

    registration_model.update_registration_mode(
        registration_mode
    )

    request.session["message"] = "新規登録方式を保存しました。"

    return RedirectResponse(
        "/admin/system/registration",
        status_code=303
    )
