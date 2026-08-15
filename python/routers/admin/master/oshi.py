from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.admin.master import oshi as oshi_model

router = APIRouter(
    prefix="/admin/master/oshi",
    tags=["admin_master_oshi"]
)


@router.get("")
async def oshi_list(
        request: Request
):
    if not auth.is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    oshi = oshi_model.get_oshi()

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/oshi/index.html",
        context={
            "oshi": oshi
        }
    )


@router.get("/form")
async def oshi_form(
        request: Request
):
    if not auth.is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    oshi = oshi_model.get_oshi()

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/oshi/form.html",
        context={
            "oshi": oshi
        }
    )


@router.post("/save")
async def oshi_save(
        request: Request,
        oshi_name: str = Form(...),
        birthday: str = Form(...),
        voice_actor_debut_date: str = Form(...),
        singer_debut_date: str = Form(""),
        profile_image: str = Form(""),
        profile_message: str = Form("")
):
    if not auth.is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    oshi_model.save_oshi(
        oshi_name,
        birthday,
        voice_actor_debut_date,
        singer_debut_date,
        profile_image,
        profile_message
    )

    return RedirectResponse(
        "/admin/master/oshi",
        status_code=303
    )
