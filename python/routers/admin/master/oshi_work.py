from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.admin.master import oshi_work as oshi_work_model


router = APIRouter(
    prefix="/admin/master/oshi_work",
    tags=["admin_master_oshi_work"]
)


WORK_TYPES = [
    ("ANIME", "アニメ"),
    ("MOVIE", "映画"),
    ("GAME", "ゲーム"),
    ("DRAMA", "ドラマCD"),
    ("OTHER", "その他")
]


BROADCAST_SEASONS = [
    ("SPRING", "春"),
    ("SUMMER", "夏"),
    ("AUTUMN", "秋"),
    ("WINTER", "冬")
]


def is_admin(request: Request):
    if not auth.is_login(request):
        return False

    return auth.is_admin(request)


def get_work_dates(form, work_type):
    if work_type == "ANIME":
        broadcast_year = form.get(
            "broadcast_year"
        )

        broadcast_season = form.get(
            "broadcast_season"
        )

        try:
            broadcast_year = (
                int(broadcast_year)
                if broadcast_year
                else None
            )
        except ValueError:
            broadcast_year = None

        if broadcast_season not in {
            "SPRING",
            "SUMMER",
            "AUTUMN",
            "WINTER"
        }:
            broadcast_season = None

        return (
            None,
            broadcast_year,
            broadcast_season
        )

    release_date = (
        form.get("release_date")
        or None
    )

    return (
        release_date,
        None,
        None
    )


@router.get("")
async def work_list(
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
        "created"
    )

    valid_sorts = {
        "created",
        "release_asc",
        "release_desc",
        "name",
        "updated"
    }

    if sort not in valid_sorts:
        sort = "created"

    works = oshi_work_model.get_work_list(
        keyword=keyword,
        sort=sort
    )

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/oshi_work/index.html",
        context={
            "works": works,
            "keyword": keyword,
            "sort": sort
        }
    )


@router.get("/create")
async def work_create(
        request: Request
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/oshi_work/form.html",
        context={
            "work": None,
            "work_types": WORK_TYPES,
            "broadcast_seasons": BROADCAST_SEASONS,
            "mode": "create"
        }
    )


@router.post("/create")
async def work_create_post(
        request: Request
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    form = await request.form()

    work_name = form.get(
        "work_name",
        ""
    ).strip()

    work_type = form.get(
        "work_type",
        ""
    ).strip()

    character_name = form.get(
        "character_name",
        ""
    ).strip() or None

    release_date, broadcast_year, broadcast_season = (
        get_work_dates(
            form,
            work_type
        )
    )

    official_url = (
        form.get("official_url", "").strip()
        or None
    )

    description = (
        form.get("description", "").strip()
        or None
    )

    public_flag = (
        form.get("public_flag") == "on"
    )

    oshi_work_model.create_work(
        work_name=work_name,
        work_type=work_type,
        character_name=character_name,
        release_date=release_date,
        broadcast_year=broadcast_year,
        broadcast_season=broadcast_season,
        official_url=official_url,
        description=description,
        public_flag=public_flag
    )

    return RedirectResponse(
        "/admin/master/oshi_work",
        status_code=303
    )


@router.get("/edit/{work_id}")
async def work_edit(
        request: Request,
        work_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    work = oshi_work_model.get_work(
        work_id
    )

    if work is None:
        return RedirectResponse(
            "/admin/master/oshi_work",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/oshi_work/form.html",
        context={
            "work": work,
            "work_types": WORK_TYPES,
            "broadcast_seasons": BROADCAST_SEASONS,
            "mode": "edit"
        }
    )


@router.post("/edit/{work_id}")
async def work_edit_post(
        request: Request,
        work_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    form = await request.form()

    work_name = form.get(
        "work_name",
        ""
    ).strip()

    work_type = form.get(
        "work_type",
        ""
    ).strip()

    character_name = form.get(
        "character_name",
        ""
    ).strip() or None

    release_date, broadcast_year, broadcast_season = (
        get_work_dates(
            form,
            work_type
        )
    )

    official_url = (
        form.get("official_url", "").strip()
        or None
    )

    description = (
        form.get("description", "").strip()
        or None
    )

    public_flag = (
        form.get("public_flag") == "on"
    )

    oshi_work_model.update_work(
        work_id=work_id,
        work_name=work_name,
        work_type=work_type,
        character_name=character_name,
        release_date=release_date,
        broadcast_year=broadcast_year,
        broadcast_season=broadcast_season,
        official_url=official_url,
        description=description,
        public_flag=public_flag
    )

    return RedirectResponse(
        "/admin/master/oshi_work",
        status_code=303
    )


@router.get("/delete/{work_id}")
async def work_delete(
        request: Request,
        work_id: int
):
    if not is_admin(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    oshi_work_model.delete_work(
        work_id
    )

    return RedirectResponse(
        "/admin/master/oshi_work",
        status_code=303
    )
