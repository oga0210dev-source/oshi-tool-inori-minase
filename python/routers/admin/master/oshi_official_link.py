from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.admin.master import oshi_official_link as oshi_official_link_model


router = APIRouter(
    prefix="/admin/master/oshi_official_link",
    tags=["admin_master_oshi_official_link"]
)


def is_admin(request: Request):
    if not auth.is_login(request):
        return False

    return auth.is_admin(request)


@router.get("")
async def official_link_list(
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
        "display"
    )

    valid_sorts = {
        "display",
        "name",
        "created",
        "updated"
    }

    if sort not in valid_sorts:
        sort = "display"

    links = (
        oshi_official_link_model.get_official_link_list(
            keyword=keyword,
            sort=sort
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/oshi_official_link/index.html",
        context={
            "links": links,
            "keyword": keyword,
            "sort": sort
        }
    )


@router.get("/create")
async def official_link_create(
        request: Request
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/oshi_official_link/form.html",
        context={
            "link": None,
            "mode": "create"
        }
    )


@router.post("/create")
async def official_link_create_post(
        request: Request
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    form = await request.form()

    link_name = form.get(
        "link_name",
        ""
    ).strip()

    url = form.get(
        "url",
        ""
    ).strip()

    icon = (
        form.get("icon", "").strip()
        or None
    )

    description = (
        form.get("description", "").strip()
        or None
    )

    public_flag = (
        form.get("public_flag") == "on"
    )

    oshi_official_link_model.create_official_link(
        link_name=link_name,
        url=url,
        icon=icon,
        description=description,
        public_flag=public_flag
    )

    return RedirectResponse(
        "/admin/master/oshi_official_link",
        status_code=303
    )


@router.get("/edit/{link_id}")
async def official_link_edit(
        request: Request,
        link_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    link = (
        oshi_official_link_model.get_official_link(
            link_id
        )
    )

    if link is None:
        return RedirectResponse(
            "/admin/master/oshi_official_link",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/oshi_official_link/form.html",
        context={
            "link": link,
            "mode": "edit"
        }
    )


@router.post("/edit/{link_id}")
async def official_link_edit_post(
        request: Request,
        link_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    form = await request.form()

    link_name = form.get(
        "link_name",
        ""
    ).strip()

    url = form.get(
        "url",
        ""
    ).strip()

    icon = (
        form.get("icon", "").strip()
        or None
    )

    description = (
        form.get("description", "").strip()
        or None
    )

    public_flag = (
        form.get("public_flag") == "on"
    )

    oshi_official_link_model.update_official_link(
        link_id=link_id,
        link_name=link_name,
        url=url,
        icon=icon,
        description=description,
        public_flag=public_flag
    )

    return RedirectResponse(
        "/admin/master/oshi_official_link",
        status_code=303
    )


@router.get("/delete/{link_id}")
async def official_link_delete(
        request: Request,
        link_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    oshi_official_link_model.delete_official_link(
        link_id
    )

    return RedirectResponse(
        "/admin/master/oshi_official_link",
        status_code=303
    )
