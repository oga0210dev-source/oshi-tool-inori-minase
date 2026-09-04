from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.admin.master import announcement as announcement_model


router = APIRouter(
    prefix="/admin/master/announcement",
    tags=["admin_master_announcement"]
)


GENRE_LIST = [
    {"value": "NOTICE", "label": "お知らせ"},
    {"value": "UPDATE", "label": "アップデート"},
    {"value": "BUG", "label": "不具合"},
    {"value": "MAINTENANCE", "label": "メンテナンス"}
]


def check_admin(request: Request):
    """
    管理者チェック
    """

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    return None


@router.get("")
async def announcement_list(
        request: Request,
        keyword: str = None,
        genre: str = None,
        status: str = None
):
    redirect = check_admin(request)

    if redirect:
        return redirect

    announcements = announcement_model.get_announcement_list(
        keyword=keyword,
        genre=genre,
        status=status
    )

    return render(
        request=request,
        name="templates/admin/master/announcement/index.html",
        context={
            "announcements": announcements,
            "keyword": keyword,
            "genre": genre,
            "status": status,
            "genre_list": GENRE_LIST
        }
    )


@router.get("/create")
async def announcement_create_page(
        request: Request
):
    redirect = check_admin(request)

    if redirect:
        return redirect

    return render(
        request=request,
        name="templates/admin/master/announcement/form.html",
        context={
            "announcement": None,
            "genre_list": GENRE_LIST
        }
    )


@router.post("/create")
async def announcement_create(
        request: Request,

        genre: str = Form(...),
        priority: int = Form(3),
        title: str = Form(...),
        body: str = Form(...),
        start_at: str = Form(...),
        end_at: str = Form(None),
        is_active: bool = Form(False)
):
    redirect = check_admin(request)

    if redirect:
        return redirect

    announcement_data = {
        "genre": genre,
        "priority": priority,
        "title": title,
        "body": body,
        "start_at": start_at,
        "end_at": end_at or None,
        "is_active": is_active
    }

    if genre not in [
        item["value"]
        for item in GENRE_LIST
    ]:
        return render(
            request=request,
            name="templates/admin/master/announcement/form.html",
            context={
                "error": "ジャンルを選択してください",
                "announcement": announcement_data,
                "genre_list": GENRE_LIST
            }
        )

    if not title.strip():
        return render(
            request=request,
            name="templates/admin/master/announcement/form.html",
            context={
                "error": "件名を入力してください",
                "announcement": announcement_data,
                "genre_list": GENRE_LIST
            }
        )

    if not body.strip():
        return render(
            request=request,
            name="templates/admin/master/announcement/form.html",
            context={
                "error": "本文を入力してください",
                "announcement": announcement_data,
                "genre_list": GENRE_LIST
            }
        )

    if priority < 1:
        return render(
            request=request,
            name="templates/admin/master/announcement/form.html",
            context={
                "error": "優先度は1以上で入力してください",
                "announcement": announcement_data,
                "genre_list": GENRE_LIST
            }
        )

    announcement_model.create_announcement(
        announcement_data
    )

    return RedirectResponse(
        "/admin/master/announcement",
        status_code=303
    )


@router.get("/edit/{announcement_id}")
async def announcement_edit_page(
        request: Request,
        announcement_id: int
):
    redirect = check_admin(request)

    if redirect:
        return redirect

    announcement = announcement_model.get_announcement(
        announcement_id
    )

    if not announcement:
        return RedirectResponse(
            "/admin/master/announcement",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/announcement/form.html",
        context={
            "announcement": announcement,
            "genre_list": GENRE_LIST
        }
    )


@router.post("/update/{announcement_id}")
async def announcement_update(
        request: Request,
        announcement_id: int,

        genre: str = Form(...),
        priority: int = Form(3),
        title: str = Form(...),
        body: str = Form(...),
        start_at: str = Form(...),
        end_at: str = Form(None),
        is_active: bool = Form(False)
):
    redirect = check_admin(request)

    if redirect:
        return redirect

    announcement_data = {
        "genre": genre,
        "priority": priority,
        "title": title,
        "body": body,
        "start_at": start_at,
        "end_at": end_at or None,
        "is_active": is_active
    }

    if genre not in [
        item["value"]
        for item in GENRE_LIST
    ]:
        return render(
            request=request,
            name="templates/admin/master/announcement/form.html",
            context={
                "error": "ジャンルを選択してください",
                "announcement": announcement_data,
                "genre_list": GENRE_LIST
            }
        )

    if not title.strip():
        return render(
            request=request,
            name="templates/admin/master/announcement/form.html",
            context={
                "error": "件名を入力してください",
                "announcement": announcement_data,
                "genre_list": GENRE_LIST
            }
        )

    if not body.strip():
        return render(
            request=request,
            name="templates/admin/master/announcement/form.html",
            context={
                "error": "本文を入力してください",
                "announcement": announcement_data,
                "genre_list": GENRE_LIST
            }
        )

    if priority < 1:
        return render(
            request=request,
            name="templates/admin/master/announcement/form.html",
            context={
                "error": "優先度は1以上で入力してください",
                "announcement": announcement_data,
                "genre_list": GENRE_LIST
            }
        )

    announcement_model.update_announcement(
        announcement_id,
        announcement_data
    )

    return RedirectResponse(
        "/admin/master/announcement",
        status_code=303
    )


@router.get("/status/{announcement_id}")
async def announcement_status(
        request: Request,
        announcement_id: int
):
    redirect = check_admin(request)

    if redirect:
        return redirect

    announcement = announcement_model.get_announcement(
        announcement_id
    )

    if not announcement:
        return RedirectResponse(
            "/admin/master/announcement",
            status_code=303
        )

    announcement_model.update_announcement_status(
        announcement_id,
        not announcement["is_active"]
    )

    return RedirectResponse(
        "/admin/master/announcement",
        status_code=303
    )


@router.get("/delete/{announcement_id}")
async def announcement_delete(
        request: Request,
        announcement_id: int
):
    redirect = check_admin(request)

    if redirect:
        return redirect

    announcement_model.delete_announcement(
        announcement_id
    )

    return RedirectResponse(
        "/admin/master/announcement",
        status_code=303
    )
