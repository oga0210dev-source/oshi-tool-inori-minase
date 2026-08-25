from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, database, auth
from python.services.inquiry_service import (
    get_inquiry_list,
    get_inquiry_detail,
    update_inquiry
)


router = APIRouter(
    prefix="/admin/inquiry",
    tags=["admin_inquiry"]
)


@router.get("")
async def inquiry_list(request: Request):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    status = request.query_params.get("status", "")
    inquiry_type = request.query_params.get("inquiry_type", "")

    conn = database.get_connection()

    try:
        inquiries = get_inquiry_list(
            conn,
            status=status,
            inquiry_type=inquiry_type
        )
    finally:
        conn.close()

    return render(
        request=request,
        name="templates/admin/inquiry/inquiry.html",
        context={
            "request": request,
            "inquiries": inquiries,
            "status": status,
            "inquiry_type": inquiry_type
        }
    )


@router.get("/{inquiry_id}")
async def inquiry_detail(
    request: Request,
    inquiry_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    conn = database.get_connection()

    try:
        inquiry = get_inquiry_detail(
            conn=conn,
            inquiry_id=inquiry_id
        )
    finally:
        conn.close()

    if not inquiry:
        return RedirectResponse("/admin/inquiry", status_code=303)

    return render(
        request=request,
        name="templates/admin/inquiry/detail.html",
        context={
            "request": request,
            "inquiry": inquiry
        }
    )


@router.post("/{inquiry_id}")
async def inquiry_update(
    request: Request,
    inquiry_id: int,
    status: str = Form(...),
    admin_memo: str = Form("")
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    if status not in (
        "UNRESOLVED",
        "IN_PROGRESS",
        "RESOLVED"
    ):
        return RedirectResponse(
            f"/admin/inquiry/{inquiry_id}",
            status_code=303
        )

    conn = database.get_connection()

    try:
        update_inquiry(
            conn=conn,
            inquiry_id=inquiry_id,
            status=status,
            admin_memo=admin_memo.strip()
        )
    finally:
        conn.close()

    return RedirectResponse(
        f"/admin/inquiry/{inquiry_id}",
        status_code=303
    )
