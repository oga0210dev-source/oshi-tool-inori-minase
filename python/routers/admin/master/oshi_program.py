from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.admin.master import oshi_program as program_model
from python.utils.validator import is_valid_url


router = APIRouter(
    prefix="/admin/master/oshi_program",
    tags=["admin_master_oshi_program"]
)


@router.get("")
async def program_list(
        request: Request,
        keyword: str = None,
        program_type: str = None,
        sort: str = "display"
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    programs = program_model.get_program_list(
        keyword,
        program_type,
        sort
    )

    return render(
        request=request,
        name="templates/admin/master/oshi_program/index.html",
        context={
            "programs": programs,
            "keyword": keyword,
            "program_type": program_type,
            "sort": sort
        }
    )


@router.get("/create")
async def program_create_page(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    return render(
        request=request,
        name="templates/admin/master/oshi_program/form.html",
        context={
            "program": None
        }
    )


@router.post("/create")
async def program_create(
        request: Request,
        program_name: str = Form(...),
        program_type: str = Form(...),
        start_date: str = Form(None),
        end_date: str = Form(None),
        official_url: str = Form(None),
        description: str = Form(None),
        public_flag: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    program_data = {
        "program_name": program_name,
        "program_type": program_type,
        "start_date": start_date,
        "end_date": end_date,
        "official_url": official_url,
        "description": description,
        "public_flag": public_flag
    }

    if not program_name.strip():
        return render(
            request=request,
            name="templates/admin/master/oshi_program/form.html",
            context={
                "error": "番組名を入力してください",
                "program": program_data
            }
        )

    if program_type not in [
        "RADIO",
        "TV",
        "WEB",
        "OTHER"
    ]:
        return render(
            request=request,
            name="templates/admin/master/oshi_program/form.html",
            context={
                "error": "番組種別が正しくありません",
                "program": program_data
            }
        )

    if not is_valid_url(official_url):
        return render(
            request=request,
            name="templates/admin/master/oshi_program/form.html",
            context={
                "error": "公式サイトURLの形式が正しくありません",
                "program": program_data
            }
        )

    if start_date and end_date and start_date > end_date:
        return render(
            request=request,
            name="templates/admin/master/oshi_program/form.html",
            context={
                "error": "終了日は開始日以降の日付を指定してください",
                "program": program_data
            }
        )

    program_model.create_program(
        program_data
    )

    return RedirectResponse(
        "/admin/master/oshi_program",
        status_code=303
    )


@router.get("/edit/{program_id}")
async def program_edit_page(
        request: Request,
        program_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    program = program_model.get_program(
        program_id
    )

    if not program:
        return RedirectResponse(
            "/admin/master/oshi_program",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/oshi_program/form.html",
        context={
            "program": program
        }
    )


@router.post("/update/{program_id}")
async def program_update(
        request: Request,
        program_id: int,
        program_name: str = Form(...),
        program_type: str = Form(...),
        start_date: str = Form(None),
        end_date: str = Form(None),
        official_url: str = Form(None),
        description: str = Form(None),
        public_flag: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    program_data = {
        "program_name": program_name,
        "program_type": program_type,
        "start_date": start_date,
        "end_date": end_date,
        "official_url": official_url,
        "description": description,
        "public_flag": public_flag
    }

    if not program_name.strip():
        return render(
            request=request,
            name="templates/admin/master/oshi_program/form.html",
            context={
                "error": "番組名を入力してください",
                "program": program_data
            }
        )

    if program_type not in [
        "RADIO",
        "TV",
        "WEB",
        "OTHER"
    ]:
        return render(
            request=request,
            name="templates/admin/master/oshi_program/form.html",
            context={
                "error": "番組種別が正しくありません",
                "program": program_data
            }
        )

    if not is_valid_url(official_url):
        return render(
            request=request,
            name="templates/admin/master/oshi_program/form.html",
            context={
                "error": "公式サイトURLの形式が正しくありません",
                "program": program_data
            }
        )

    if start_date and end_date and start_date > end_date:
        return render(
            request=request,
            name="templates/admin/master/oshi_program/form.html",
            context={
                "error": "終了日は開始日以降の日付を指定してください",
                "program": program_data
            }
        )

    program_model.update_program(
        program_id,
        program_data
    )

    return RedirectResponse(
        "/admin/master/oshi_program",
        status_code=303
    )


@router.get("/delete/{program_id}")
async def program_delete(
        request: Request,
        program_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    program_model.delete_program(
        program_id
    )

    return RedirectResponse(
        "/admin/master/oshi_program",
        status_code=303
    )
