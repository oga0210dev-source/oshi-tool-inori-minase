from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render
from python.core import auth

from python.models.admin.master import oshi_anniversary as oshi_anniversary_model


router = APIRouter(
    prefix="/admin/master/oshi_anniversary",
    tags=["admin_master_oshi_anniversary"]
)


def is_admin(request: Request):
    if not auth.is_login(request):
        return False

    return auth.is_admin(request)


@router.get("")
async def anniversary_list(
        request: Request
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    keyword = request.query_params.get(
        "keyword",
        ""
    ).strip()

    sort = request.query_params.get(
        "sort",
        "date_asc"
    )

    valid_sorts = {
        "date_asc",
        "date_desc",
        "display_order",
        "name",
        "created",
        "updated"
    }

    if sort not in valid_sorts:
        sort = "date_asc"

    anniversaries = (
        oshi_anniversary_model.get_anniversary_list(
            keyword=keyword,
            sort=sort
        )
    )

    return render(
        request=request,
        name="templates/admin/master/oshi_anniversary/index.html",
        context={
            "anniversaries": anniversaries,
            "keyword": keyword,
            "sort": sort
        }
    )


@router.get("/create")
async def anniversary_create(
        request: Request
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/oshi_anniversary/form.html",
        context={
            "anniversary": None,
            "mode": "create"
        }
    )


@router.post("/create")
async def anniversary_create_post(
        request: Request
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    form = await request.form()

    anniversary_name = form.get(
        "anniversary_name",
        ""
    ).strip()

    anniversary_date = (
        form.get("anniversary_date")
        or None
    )

    description = (
        form.get("description", "").strip()
        or None
    )

    public_flag = (
        form.get("public_flag") == "on"
    )

    oshi_anniversary_model.create_anniversary(
        anniversary_name=anniversary_name,
        anniversary_date=anniversary_date,
        description=description,
        public_flag=public_flag
    )

    return RedirectResponse(
        "/admin/master/oshi_anniversary",
        status_code=303
    )


@router.get("/edit/{anniversary_id}")
async def anniversary_edit(
        request: Request,
        anniversary_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    anniversary = (
        oshi_anniversary_model.get_anniversary(
            anniversary_id
        )
    )

    if anniversary is None:
        return RedirectResponse(
            "/admin/master/oshi_anniversary",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/oshi_anniversary/form.html",
        context={
            "anniversary": anniversary,
            "mode": "edit"
        }
    )


@router.post("/edit/{anniversary_id}")
async def anniversary_edit_post(
        request: Request,
        anniversary_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    form = await request.form()

    anniversary_name = form.get(
        "anniversary_name",
        ""
    ).strip()

    anniversary_date = (
        form.get("anniversary_date")
        or None
    )

    description = (
        form.get("description", "").strip()
        or None
    )

    public_flag = (
        form.get("public_flag") == "on"
    )

    oshi_anniversary_model.update_anniversary(
        anniversary_id=anniversary_id,
        anniversary_name=anniversary_name,
        anniversary_date=anniversary_date,
        description=description,
        public_flag=public_flag
    )

    return RedirectResponse(
        "/admin/master/oshi_anniversary",
        status_code=303
    )


@router.get("/delete/{anniversary_id}")
async def anniversary_delete(
        request: Request,
        anniversary_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    oshi_anniversary_model.delete_anniversary(
        anniversary_id
    )

    return RedirectResponse(
        "/admin/master/oshi_anniversary",
        status_code=303
    )
