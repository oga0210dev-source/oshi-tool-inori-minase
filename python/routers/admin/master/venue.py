from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.admin.master import venue as venue_model
from python.models.admin.master.master import get_prefecture_list
from python.utils.validator import is_valid_url

from collections import OrderedDict


router = APIRouter(
    prefix="/admin/master/venue",
    tags=["admin_master_venue"]
)


def get_prefecture_groups():
    prefecture_groups = OrderedDict()

    for prefecture in get_prefecture_list():
        area = prefecture["area_name"]

        if area not in prefecture_groups:
            prefecture_groups[area] = []

        prefecture_groups[area].append(prefecture)

    return prefecture_groups


@router.get("")
async def venue_list(
        request: Request,
        keyword: str = None,
        sort: str = "name"
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    venues = venue_model.get_venue_list(
        keyword,
        sort
    )

    return render(
        request=request,
        name="templates/admin/master/venue/index.html",
        context={
            "venues": venues,
            "keyword": keyword,
            "sort": sort
        }
    )


@router.get("/create")
async def venue_create_page(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    return render(
        request=request,
        name="templates/admin/master/venue/form.html",
        context={
            "venue": None,
            "prefecture_groups": get_prefecture_groups()
        }
    )


@router.post("/create")
async def venue_create(
        request: Request,

        venue_name: str = Form(...),
        address: str = Form(...),
        prefecture_code: int = Form(None),
        latitude: float = Form(None),
        longitude: float = Form(None),
        public_flag: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    venue_data = {
        "venue_name": venue_name,
        "address": address,
        "prefecture_code": prefecture_code,
        "latitude": latitude,
        "longitude": longitude,
        "public_flag": public_flag
    }

    if not venue_name.strip():
        return render(
            request=request,
            name="templates/admin/master/venue/form.html",
            context={
                "error": "会場名を入力してください",
                "venue": venue_data,
                "prefecture_groups": get_prefecture_groups()
            }
        )

    if not address.strip():
        return render(
            request=request,
            name="templates/admin/master/venue/form.html",
            context={
                "error": "住所を入力してください",
                "venue": venue_data,
                "prefecture_groups": get_prefecture_groups()
            }
        )

    venue_model.create_venue(
        venue_data
    )

    return RedirectResponse(
        "/admin/master/venue",
        status_code=303
    )


@router.get("/edit/{venue_id}")
async def venue_edit_page(
        request: Request,
        venue_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    venue = venue_model.get_venue(
        venue_id
    )

    if not venue:
        return RedirectResponse(
            "/admin/master/venue",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/venue/form.html",
        context={
            "venue": venue,
            "prefecture_groups": get_prefecture_groups()
        }
    )


@router.post("/update/{venue_id}")
async def venue_update(
        request: Request,
        venue_id: int,

        venue_name: str = Form(...),
        address: str = Form(...),
        prefecture_code: int = Form(None),
        latitude: float = Form(None),
        longitude: float = Form(None),
        public_flag: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    venue_data = {
        "venue_name": venue_name,
        "address": address,
        "prefecture_code": prefecture_code,
        "latitude": latitude,
        "longitude": longitude,
        "public_flag": public_flag
    }

    if not venue_name.strip():
        return render(
            request=request,
            name="templates/admin/master/venue/form.html",
            context={
                "error": "会場名を入力してください",
                "venue": venue_data,
                "prefecture_groups": get_prefecture_groups()
            }
        )

    if not address.strip():
        return render(
            request=request,
            name="templates/admin/master/venue/form.html",
            context={
                "error": "住所を入力してください",
                "venue": venue_data,
                "prefecture_groups": get_prefecture_groups()
            }
        )

    venue_model.update_venue(
        venue_id,
        venue_data
    )

    return RedirectResponse(
        "/admin/master/venue",
        status_code=303
    )


@router.get("/delete/{venue_id}")
async def venue_delete(
        request: Request,
        venue_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    venue_model.delete_venue(
        venue_id
    )

    return RedirectResponse(
        "/admin/master/venue",
        status_code=303
    )
