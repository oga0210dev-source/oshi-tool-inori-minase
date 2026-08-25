from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from python.core import render, database

from python.services.inquiry_service import create_inquiry


router = APIRouter(
    prefix="/home/inquiry",
    tags=["home_inquiry"]
)


@router.get("")
async def inquiry_page(request: Request):

    return render(
        request=request,
        name="templates/home/inquiry/inquiry.html"
    )


@router.post("")
async def inquiry_submit(
    request: Request,
    inquiry_type: str = Form(...),
    subject: str = Form(...),
    email: str = Form(""),
    message: str = Form(...)
):

    user_id = request.session.get("user_id")

    # 未ログインの場合
    if not user_id:
        user_id = "GUEST"

    if inquiry_type == "INQUIRY" and not email.strip():
        return render(
            request=request,
            name="templates/home/inquiry/inquiry.html",
            context={
                "error": "問い合わせの場合はメールアドレスを入力してください。",
                "inquiry_type": inquiry_type,
                "subject": subject,
                "email": email,
                "message": message
            },
            status_code=400
        )

    conn = database.get_connection()

    try:
        inquiry_id = create_inquiry(
            conn=conn,
            user_id=user_id,
            inquiry_type=inquiry_type,
            subject=subject.strip(),
            email=email.strip(),
            message=message.strip()
        )
    finally:
        conn.close()

    return RedirectResponse(
        f"/home/inquiry/complete?inquiry_id={inquiry_id}",
        status_code=303
    )


@router.get("/complete")
async def inquiry_complete(
    request: Request,
    inquiry_id: int
):

    is_login = bool(request.session.get("user_id"))

    return render(
        request=request,
        name="templates/home/inquiry/complete.html",
        context={
            "inquiry_id": inquiry_id,
            "is_login": is_login
        }
    )
