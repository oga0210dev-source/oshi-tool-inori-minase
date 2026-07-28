from fastapi import (
    APIRouter,
    Request,
    Form,
    UploadFile,
    File
)
from fastapi.responses import RedirectResponse

from python.core import templates
from python.models.user import UserModel
from python.models.image import ImageModel
from python.models.master import get_prefecture_list
from collections import OrderedDict

router = APIRouter()


@router.get("/mypage")
def mypage(request: Request):
    """マイページ表示"""

    user_id = request.session.get("user_id")

    if user_id is None:
        return RedirectResponse("/login", status_code=303)

    user = UserModel.get_user(user_id)
    prefecture_list = get_prefecture_list()
    prefecture_groups = OrderedDict()
    for prefecture in prefecture_list:
        area = prefecture["area_name"]
        if area not in prefecture_groups:
            prefecture_groups[area] = []
        prefecture_groups[area].append(prefecture)

    return templates.TemplateResponse(
        request=request,
        name="templates/mypage/mypage.html",
        context={
            "user": user,
            "prefecture_groups": prefecture_groups
        }
    )


@router.post("/mypage/update")
async def update_mypage(
    request: Request,

    user_name: str = Form(...),
    member_since: str = Form(""),
    email: str = Form(""),
    gender: str = Form(""),
    birthday: str = Form(""),

    prefecture: int = Form(0),

    x_account: str = Form(""),
    instagram_account: str = Form(""),
    discord_account: str = Form(""),

    profile_message: str = Form(""),

    profile_image: UploadFile | None = File(None)
):
    """マイページ更新"""

    user_id = request.session.get("user_id")

    if user_id is None:
        return RedirectResponse("/login", status_code=303)

    # 空文字をNULLへ変換
    member_since = member_since or None
    birthday = birthday or None
    email = email or None
    gender = gender or None
    x_account = x_account or None
    instagram_account = instagram_account or None
    discord_account = discord_account or None
    profile_message = profile_message or None

    image_url = None

    # プロフィール画像アップロード
    if profile_image and profile_image.filename:

        image_data = await profile_image.read()

        image_url = ImageModel.upload_profile_image(
            user_id=user_id,
            file_data=image_data,
            content_type=profile_image.content_type
        )

    # ユーザー情報更新
    UserModel.update_user(
        user_id=user_id,
        user_name=user_name,
        member_since=member_since,
        email=email,
        gender=gender,
        birthday=birthday,
        prefecture=prefecture,
        x_account=x_account,
        instagram_account=instagram_account,
        discord_account=discord_account,
        profile_message=profile_message,
        profile_image=image_url
    )

    return RedirectResponse(
        "/mypage",
        status_code=303
    )
