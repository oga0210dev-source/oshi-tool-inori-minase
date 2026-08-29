from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse

from python.core import render, auth

from python.models.admin.master import venue as venue_model
from python.models.admin.master.master import get_prefecture_list
from python.utils.validator import is_valid_url

from collections import OrderedDict

import urllib.parse
import urllib.request
import json


router = APIRouter(
    prefix="/admin/master/venue",
    tags=["admin_master_venue"]
)


@router.get("/geocode")
async def venue_geocode(
        request: Request,
        address: str
):
    if not auth.is_login(request):
        return JSONResponse(
            {
                "success": False,
                "message": "ログインしてください"
            },
            status_code=401
        )

    if not auth.is_admin(request):
        return JSONResponse(
            {
                "success": False,
                "message": "権限がありません"
            },
            status_code=403
        )

    address = address.strip()

    if not address:
        return JSONResponse(
            {
                "success": False,
                "message": "住所を入力してください"
            },
            status_code=400
        )

    try:
        params = urllib.parse.urlencode({
            "q": address
        })

        url = (
            "https://msearch.gsi.go.jp/"
            "address-search/AddressSearch?"
            + params
        )

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "oshi-tool-inori-minase"
            }
        )

        with urllib.request.urlopen(
                req,
                timeout=10
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        if not data:
            return JSONResponse({
                "success": False,
                "message": "住所から座標を取得できませんでした"
            })

        result = data[0]

        coordinates = (
            result
            .get("geometry", {})
            .get("coordinates", [])
        )

        if len(coordinates) < 2:
            return JSONResponse({
                "success": False,
                "message": "座標情報を取得できませんでした"
            })

        # 国土地理院APIは [経度, 緯度]
        longitude = coordinates[0]
        latitude = coordinates[1]

        return JSONResponse({
            "success": True,
            "latitude": latitude,
            "longitude": longitude,
            "title": result.get(
                "properties", {}
            ).get("title")
        })

    except Exception:
        return JSONResponse({
            "success": False,
            "message": "座標の取得に失敗しました"
        })


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
        capacity: int = Form(None),
        official_url: str = Form(None),
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
        "capacity": capacity,
        "official_url": official_url,
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
        capacity: int = Form(None),
        official_url: str = Form(None),
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
        "capacity": capacity,
        "official_url": official_url,
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

    if official_url and not is_valid_url(official_url):
        return render(
            request=request,
            name="templates/admin/master/venue/form.html",
            context={
                "error": "正しいURLを入力してください",
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
