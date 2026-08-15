from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from python.core import templates, database, auth

from python.services.inquiry_service import create_inquiry


router = APIRouter(
    prefix="/home/inquiry",
    tags=["home_inquiry"]
)


@router.get("")
async def inquiry_page(request: Request):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
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
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    user_id = request.session.get("user_id")

    if inquiry_type == "INQUIRY" and not email.strip():
        return templates.TemplateResponse(
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
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="templates/home/inquiry/complete.html",
        context={
            "inquiry_id": inquiry_id
        }
    )
