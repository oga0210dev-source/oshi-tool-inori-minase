from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.admin.master import meeting as meeting_model
from python.models.admin.master.master import get_venue_list
from python.utils.validator import is_valid_url


router = APIRouter(
    prefix="/admin/master/meeting",
    tags=["admin_master_meeting"]
)


@router.get("")
async def meeting_list(
        request: Request,
        keyword: str = None,
        sort: str = "date"
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    meetings = meeting_model.get_meeting_list(
        keyword,
        sort
    )

    return render(
        request=request,
        name="templates/admin/master/meeting/index.html",
        context={
            "meetings": meetings,
            "keyword": keyword,
            "sort": sort
        }
    )


@router.get("/create")
async def meeting_create_page(request: Request):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    return render(
        request=request,
        name="templates/admin/master/meeting/form.html",
        context={
            "meeting": None,
            "venues": get_venue_list()
        }
    )


@router.post("/create")
async def meeting_create(
        request: Request,

        meeting_name: str = Form(...),
        meeting_date: str = Form(...),
        performance_type: str = Form(...),
        venue_id: int = Form(...),
        official_url: str = Form(None),
        public_flag: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    meeting_data = {
        "meeting_name": meeting_name,
        "meeting_date": meeting_date,
        "performance_type": performance_type,
        "venue_id": venue_id,
        "official_url": official_url,
        "public_flag": public_flag
    }

    if not meeting_name.strip():
        return render(
            request=request,
            name="templates/admin/master/meeting/form.html",
            context={
                "error": "町民集会名を入力してください",
                "meeting": meeting_data,
                "venues": get_venue_list()
            }
        )

    if not venue_id:
        return render(
            request=request,
            name="templates/admin/master/meeting/form.html",
            context={
                "error": "会場を選択してください",
                "meeting": meeting_data,
                "venues": get_venue_list()
            }
        )

    if performance_type not in [
        "DAY",
        "NIGHT",
        "PART1",
        "PART2",
        "PART3"
    ]:
        return render(
            request=request,
            name="templates/admin/master/meeting/form.html",
            context={
                "error": "公演区分が正しくありません",
                "meeting": meeting_data,
                "venues": get_venue_list()
            }
        )

    if not is_valid_url(official_url):
        return render(
            request=request,
            name="templates/admin/master/meeting/form.html",
            context={
                "error": "公式サイトURLの形式が正しくありません",
                "meeting": meeting_data,
                "venues": get_venue_list()
            }
        )

    meeting_model.create_meeting(
        meeting_data
    )

    return RedirectResponse(
        "/admin/master/meeting",
        status_code=303
    )


@router.get("/edit/{meeting_id}")
async def meeting_edit_page(
        request: Request,
        meeting_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    meeting = meeting_model.get_meeting(
        meeting_id
    )

    if not meeting:
        return RedirectResponse(
            "/admin/master/meeting",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/meeting/form.html",
        context={
            "meeting": meeting,
            "venues": get_venue_list()
        }
    )


@router.post("/update/{meeting_id}")
async def meeting_update(
        request: Request,
        meeting_id: int,

        meeting_name: str = Form(...),
        meeting_date: str = Form(...),
        performance_type: str = Form(...),
        venue_id: int = Form(...),
        official_url: str = Form(None),
        public_flag: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    meeting_data = {
        "meeting_name": meeting_name,
        "meeting_date": meeting_date,
        "performance_type": performance_type,
        "venue_id": venue_id,
        "official_url": official_url,
        "public_flag": public_flag
    }

    if not meeting_name.strip():
        return render(
            request=request,
            name="templates/admin/master/meeting/form.html",
            context={
                "error": "町民集会名を入力してください",
                "meeting": meeting_data,
                "venues": get_venue_list()
            }
        )

    if not venue_id:
        return render(
            request=request,
            name="templates/admin/master/meeting/form.html",
            context={
                "error": "会場を選択してください",
                "meeting": meeting_data,
                "venues": get_venue_list()
            }
        )

    if performance_type not in [
        "DAY",
        "NIGHT",
        "PART1",
        "PART2",
        "PART3"
    ]:
        return render(
            request=request,
            name="templates/admin/master/meeting/form.html",
            context={
                "error": "公演区分が正しくありません",
                "meeting": meeting_data,
                "venues": get_venue_list()
            }
        )

    if not is_valid_url(official_url):
        return render(
            request=request,
            name="templates/admin/master/meeting/form.html",
            context={
                "error": "公式サイトURLの形式が正しくありません",
                "meeting": meeting_data,
                "venues": get_venue_list()
            }
        )

    meeting_model.update_meeting(
        meeting_id,
        meeting_data
    )

    return RedirectResponse(
        "/admin/master/meeting",
        status_code=303
    )


@router.get("/delete/{meeting_id}")
async def meeting_delete(
        request: Request,
        meeting_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    meeting_model.delete_meeting(
        meeting_id
    )

    return RedirectResponse(
        "/admin/master/meeting",
        status_code=303
    )


@router.get("/{meeting_id}/guest")
async def meeting_guest_list(
        request: Request,
        meeting_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    meeting = meeting_model.get_meeting(
        meeting_id
    )

    if not meeting:
        return RedirectResponse(
            "/admin/master/meeting",
            status_code=303
        )

    guests = meeting_model.get_meeting_guests(
        meeting_id
    )

    next_display_order = len(guests) + 1

    return render(
        request=request,
        name="templates/admin/master/meeting/guest.html",
        context={
            "meeting": meeting,
            "guests": guests,
            "next_display_order": next_display_order
        }
    )


@router.post("/{meeting_id}/guest/create")
async def meeting_guest_create(
        request: Request,
        meeting_id: int,
        guest_name: str = Form(...),
        display_order: int = Form(0)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    meeting = meeting_model.get_meeting(
        meeting_id
    )

    if not meeting:
        return RedirectResponse(
            "/admin/master/meeting",
            status_code=303
        )

    if not guest_name.strip():
        return RedirectResponse(
            f"/admin/master/meeting/{meeting_id}/guest",
            status_code=303
        )

    meeting_model.create_meeting_guest(
        meeting_id,
        guest_name.strip(),
        display_order
    )

    return RedirectResponse(
        f"/admin/master/meeting/{meeting_id}/guest",
        status_code=303
    )


@router.post("/{meeting_id}/guest/update/{guest_id}")
async def meeting_guest_update(
        request: Request,
        meeting_id: int,
        guest_id: int,
        guest_name: str = Form(...),
        display_order: int = Form(0)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    if not guest_name.strip():
        return RedirectResponse(
            f"/admin/master/meeting/{meeting_id}/guest",
            status_code=303
        )

    meeting_model.update_meeting_guest(
        guest_id,
        guest_name.strip(),
        display_order
    )

    return RedirectResponse(
        f"/admin/master/meeting/{meeting_id}/guest",
        status_code=303
    )


@router.get("/{meeting_id}/guest/delete/{guest_id}")
async def meeting_guest_delete(
        request: Request,
        meeting_id: int,
        guest_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    meeting_model.delete_meeting_guest(
        guest_id
    )

    return RedirectResponse(
        f"/admin/master/meeting/{meeting_id}/guest",
        status_code=303
    )
