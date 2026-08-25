import secrets
import string

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render
from python.core import auth

from python.models.admin.master import invitation_code as invitation_code_model


router = APIRouter(
    prefix="/admin/master/invitation_code",
    tags=["admin_master_invitation_code"]
)


def generate_invitation_code(length=12):
    """
    招待コード生成
    """
    characters = string.ascii_uppercase + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


@router.get("")
async def invitation_code_list(
        request: Request
):
    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    invitation_codes = invitation_code_model.get_invitation_code_list()

    return render(
        request=request,
        name="templates/admin/master/invitation_code/index.html",
        context={
            "invitation_codes": invitation_codes
        }
    )


@router.get("/create")
async def invitation_code_create_page(
        request: Request
):
    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    invitation_code = generate_invitation_code()

    return render(
        request=request,
        name="templates/admin/master/invitation_code/form.html",
        context={
            "invitation_code": {
                "invitation_code": invitation_code,
                "max_usage": None,
                "expires_at": None,
                "is_active": True
            }
        }
    )


@router.post("/create")
async def invitation_code_create(
        request: Request,
        invitation_code: str = Form(...),
        max_usage: int = Form(None),
        expires_at: str = Form(None)
):
    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    invitation_code = invitation_code.strip()

    if not invitation_code:
        return render(
            request=request,
            name="templates/admin/master/invitation_code/form.html",
            context={
                "error": "招待コードを入力してください",
                "invitation_code": {
                    "invitation_code": invitation_code,
                    "max_usage": max_usage,
                    "expires_at": expires_at,
                    "is_active": True
                }
            }
        )

    if len(invitation_code) > 100:
        return render(
            request=request,
            name="templates/admin/master/invitation_code/form.html",
            context={
                "error": "招待コードは100文字以内で入力してください",
                "invitation_code": {
                    "invitation_code": invitation_code,
                    "max_usage": max_usage,
                    "expires_at": expires_at,
                    "is_active": True
                }
            }
        )

    if max_usage is not None and max_usage < 1:
        return render(
            request=request,
            name="templates/admin/master/invitation_code/form.html",
            context={
                "error": "最大利用回数は1以上で入力してください",
                "invitation_code": {
                    "invitation_code": invitation_code,
                    "max_usage": max_usage,
                    "expires_at": expires_at,
                    "is_active": True
                }
            }
        )

    if invitation_code_model.get_invitation_code(invitation_code):
        return render(
            request=request,
            name="templates/admin/master/invitation_code/form.html",
            context={
                "error": "同じ招待コードがすでに登録されています",
                "invitation_code": {
                    "invitation_code": invitation_code,
                    "max_usage": max_usage,
                    "expires_at": expires_at,
                    "is_active": True
                }
            }
        )

    invitation_code_model.create_invitation_code(
        invitation_code,
        max_usage,
        expires_at
    )

    return RedirectResponse(
        "/admin/master/invitation_code",
        status_code=303
    )


@router.get("/edit/{invitation_code}")
async def invitation_code_edit_page(
        request: Request,
        invitation_code: str
):
    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    code = invitation_code_model.get_invitation_code(
        invitation_code
    )

    if not code:
        return RedirectResponse(
            "/admin/master/invitation_code",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/invitation_code/form.html",
        context={
            "invitation_code": code
        }
    )


@router.post("/update/{invitation_code}")
async def invitation_code_update(
        request: Request,
        invitation_code: str,
        max_usage: int = Form(None),
        expires_at: str = Form(None),
        is_active: bool = Form(False)
):
    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    code = invitation_code_model.get_invitation_code(
        invitation_code
    )

    if not code:
        return RedirectResponse(
            "/admin/master/invitation_code",
            status_code=303
        )

    if max_usage is not None and max_usage < 1:
        return render(
            request=request,
            name="templates/admin/master/invitation_code/form.html",
            context={
                "error": "最大利用回数は1以上で入力してください",
                "invitation_code": {
                    **code,
                    "max_usage": max_usage,
                    "expires_at": expires_at,
                    "is_active": is_active
                }
            }
        )

    invitation_code_model.update_invitation_code(
        invitation_code,
        is_active,
        max_usage,
        expires_at
    )

    return RedirectResponse(
        "/admin/master/invitation_code",
        status_code=303
    )


@router.get("/toggle/{invitation_code}")
async def invitation_code_toggle(
        request: Request,
        invitation_code: str
):
    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    invitation_code_model.toggle_invitation_code(
        invitation_code
    )

    return RedirectResponse(
        "/admin/master/invitation_code",
        status_code=303
    )
