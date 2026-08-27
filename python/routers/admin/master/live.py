from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.admin.master import live as live_model
from python.utils.validator import is_valid_url
from python.models.admin.master.master import (
    get_prefecture_list,
    get_venue_list
)

from collections import OrderedDict


router = APIRouter(
    prefix="/admin/master/live",
    tags=["admin_master_live"]
)


def get_prefecture_groups():
    prefecture_groups = OrderedDict()

    for prefecture in get_prefecture_list():
        area = prefecture["area_name"]

        if area not in prefecture_groups:
            prefecture_groups[area] = []

        prefecture_groups[area].append(prefecture)

    return prefecture_groups


def group_by_tour(lives):
    """
    ツアー単位にグループ化
    """
    tours = []

    current_tour = None

    for live in lives:
        tour_name = live["tour_name"] or "ツアー未設定"

        if current_tour != tour_name:
            current_tour = tour_name

            tours.append({
                "tour_name": tour_name,
                "lives": []
            })

        tours[-1]["lives"].append(live)

    return tours


@router.get("")
async def live_list(
        request: Request,
        keyword: str = None,
        sort: str = "tour"
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    lives = live_model.get_live_list(
        keyword,
        sort
    )

    tours = group_by_tour(lives)

    return render(
        request=request,
        name="templates/admin/master/live/index.html",
        context={
            "tours": tours,
            "keyword": keyword,
            "sort": sort
        }
    )


@router.get("/create")
async def live_create_page(request: Request):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    return render(
        request=request,
        name="templates/admin/master/live/form.html",
        context={
            "live": None,
            "tour_list": live_model.get_tour_list(),
            "venue_list": get_venue_list()
        }
    )


@router.post("/create")
async def live_create(
        request: Request,

        live_name: str = Form(...),
        tour_name: str = Form(None),
        tour_order: int = Form(None),
        live_date: str = Form(...),
        venue_id: int = Form(None),
        blu_ray_url: str = Form(None),
        official_url: str = Form(None),
        public_flag: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    live_data = {
        "live_name": live_name,
        "tour_name": tour_name,
        "tour_order": tour_order,
        "live_date": live_date,
        "venue_id": venue_id,
        "blu_ray_url": blu_ray_url,
        "official_url": official_url,
        "public_flag": public_flag
    }

    if not live_name.strip():
        return render(
            request=request,
            name="templates/admin/master/live/form.html",
            context={
                "error": "ライブ名を入力してください",
                "live": live_data,
                "tour_list": live_model.get_tour_list(),
                "venue_list": get_venue_list()
            }
        )

    if not venue_id:
        return render(
            request=request,
            name="templates/admin/master/live/form.html",
            context={
                "error": "会場を選択してください",
                "live": live_data,
                "tour_list": live_model.get_tour_list(),
                "venue_list": get_venue_list()
            }
        )

    for name, url in [
        ("Blu-ray URL", blu_ray_url),
        ("公式サイトURL", official_url)
    ]:

        if not is_valid_url(url):
            return render(
                request=request,
                name="templates/admin/master/live/form.html",
                context={
                    "error": f"{name}の形式が正しくありません",
                    "live": live_data,
                    "tour_list": live_model.get_tour_list(),
                    "venue_list": get_venue_list()
                }
            )

    live_model.create_live(
        live_data
    )

    return RedirectResponse(
        "/admin/master/live",
        status_code=303
    )


@router.get("/edit/{live_id}")
async def live_edit_page(
        request: Request,
        live_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    live = live_model.get_live(live_id)

    if not live:
        return RedirectResponse(
            "/admin/master/live",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/live/form.html",
        context={
            "live": live,
            "tour_list": live_model.get_tour_list(),
            "venue_list": get_venue_list()
        }
    )


@router.post("/update/{live_id}")
async def live_update(
        request: Request,
        live_id: int,

        live_name: str = Form(...),
        tour_name: str = Form(None),
        tour_order: int = Form(None),
        live_date: str = Form(...),
        venue_id: int = Form(None),
        blu_ray_url: str = Form(None),
        official_url: str = Form(None),
        public_flag: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    live_data = {
        "live_name": live_name,
        "tour_name": tour_name,
        "tour_order": tour_order,
        "live_date": live_date,
        "venue_id": venue_id,
        "blu_ray_url": blu_ray_url,
        "official_url": official_url,
        "public_flag": public_flag
    }

    if not live_name.strip():
        return render(
            request=request,
            name="templates/admin/master/live/form.html",
            context={
                "error": "ライブ名を入力してください",
                "live": live_data,
                "tour_list": live_model.get_tour_list(),
                "venue_list": get_venue_list()
            }
        )

    if not venue_id:
        return render(
            request=request,
            name="templates/admin/master/live/form.html",
            context={
                "error": "会場を選択してください",
                "live": live_data,
                "tour_list": live_model.get_tour_list(),
                "venue_list": get_venue_list()
            }
        )

    for name, url in [
        ("Blu-ray URL", blu_ray_url),
        ("公式サイトURL", official_url)
    ]:

        if not is_valid_url(url):
            return render(
                request=request,
                name="templates/admin/master/live/form.html",
                context={
                    "error": f"{name}の形式が正しくありません",
                    "live": live_data,
                    "tour_list": live_model.get_tour_list(),
                    "venue_list": get_venue_list()
                }
            )

    live_model.update_live(
        live_id,
        live_data
    )

    return RedirectResponse(
        "/admin/master/live",
        status_code=303
    )


@router.get("/delete/{live_id}")
async def live_delete(
        request: Request,
        live_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    live_model.delete_live(
        live_id
    )

    return RedirectResponse(
        "/admin/master/live",
        status_code=303
    )
