from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from python.models.user import UserModel
from python.core import templates
from python.models.image import ImageModel
from fastapi import (
    APIRouter,
    Request,
    Form,
    UploadFile,
    File
)

router = APIRouter()


@router.get("/mypage")
def mypage(request: Request):
    user_id = request.session.get("user_id")

    if user_id is None:
        return RedirectResponse("/login")

    user = UserModel.get_user(user_id)

    return templates.TemplateResponse(
        request=request,
        name="templates/mypage/mypage.html",
        context={
            "user": user
        }
    )


@router.post("/mypage/update")
async def update(
        request: Request,
        user_name: str = Form(""),
        member_since: str = Form(""),
        email: str = Form(""),
        gender: str = Form(""),
        birthday: str = Form(""),
        profile_image: UploadFile = File(None)
):
    user_id = request.session.get("user_id")

    image_url = None

    if profile_image:
        image_data = await profile_image.read()

        image_url = ImageModel.upload_profile_image(
            user_id,
            image_data,
            profile_image.content_type
        )

    UserModel.update_user(
        user_id=user_id,
        user_name=user_name,
        member_since=member_since,
        email=email,
        gender=gender,
        birthday=birthday,
        profile_image=image_url
    )

    return RedirectResponse(
        "/mypage",
        status_code=303
    )
