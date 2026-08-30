from fastapi import (
    APIRouter,
    Request,
    Form,
    UploadFile,
    File,
    Query
)
from fastapi.responses import RedirectResponse

from python.core import render, auth
from python.core.mail import Mail
from python.core.security import Security
from python.models.user import UserModel
from python.models.image import ImageModel
from python.models.admin.master.master import get_prefecture_list

from collections import OrderedDict


router = APIRouter()


@router.get("/mypage")
def mypage(
        request: Request,
        password_changed: bool = Query(False)
):
    """マイページ表示"""

    user_id = request.session.get("user_id")

    # =====================================================
    # ログイン確認
    # =====================================================

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    user = UserModel.get_user(user_id)

    # =====================================================
    # 認証メール送信情報取得
    # =====================================================

    email_verification_sent_to = request.session.pop(
        "email_verification_sent_to",
        None
    )

    prefecture_list = get_prefecture_list()

    prefecture_groups = OrderedDict()

    for prefecture in prefecture_list:

        area = prefecture["area_name"]

        if area not in prefecture_groups:
            prefecture_groups[area] = []

        prefecture_groups[area].append(prefecture)

    return render(
        request=request,
        name="templates/mypage/mypage.html",
        context={
            "user": user,
            "prefecture_groups": prefecture_groups,
            "password_changed": password_changed,
            "email_verification_sent_to": email_verification_sent_to
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

    # =====================================================
    # ログイン確認
    # =====================================================

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    # =====================================================
    # 現在のユーザー情報取得
    # =====================================================

    current_user = UserModel.get_user(user_id)

    if not current_user:
        request.session.clear()

        return RedirectResponse(
            "/login",
            status_code=303
        )

    current_email = current_user["email"]

    # =====================================================
    # 入力値整形
    # =====================================================

    member_since = member_since or None
    birthday = birthday or None
    email = email.strip() or None
    gender = gender or None
    x_account = x_account or None
    instagram_account = instagram_account or None
    discord_account = discord_account or None
    profile_message = profile_message or None

    # =====================================================
    # メールアドレス変更確認
    # =====================================================

    email_changed = (
        current_email != email
    )

    # =====================================================
    # メールアドレス重複チェック
    # =====================================================

    if email_changed and email:

        if UserModel.exists_email(
                email=email,
                exclude_user_id=user_id
        ):
            return render(
                request=request,
                name="templates/mypage/mypage.html",
                context={
                    "user": current_user,
                    "prefecture_groups": _get_prefecture_groups(),
                    "password_changed": False,
                    "message": "このメールアドレスは既に使用されています。"
                }
            )

    # =====================================================
    # プロフィール画像
    # =====================================================

    image_url = None

    if profile_image and profile_image.filename:

        image_data = await profile_image.read()

        image_url = ImageModel.upload_profile_image(
            user_id=user_id,
            file_data=image_data,
            content_type=profile_image.content_type
        )

    # =====================================================
    # ユーザー情報更新
    # =====================================================

    # メールアドレスが変更された場合は、
    # update_user()では現在のメールアドレスを維持し、
    # 後からupdate_email()で更新する。
    #
    # これにより、メールアドレス変更処理と
    # メール認証状態の変更を分離する。

    update_email_value = current_email

    UserModel.update_user(
        user_id=user_id,
        user_name=user_name,
        member_since=member_since,
        email=update_email_value,
        gender=gender,
        birthday=birthday,
        prefecture=prefecture,
        x_account=x_account,
        instagram_account=instagram_account,
        discord_account=discord_account,
        profile_message=profile_message,
        profile_image=image_url
    )

    # =====================================================
    # メールアドレス変更
    # =====================================================

    if email_changed:

        # -------------------------------------------------
        # メールアドレスを更新
        # -------------------------------------------------

        UserModel.update_email(
            user_id=user_id,
            email=email
        )

        # -------------------------------------------------
        # 新しいメールアドレスが設定された場合
        # -------------------------------------------------

        if email:

            # 認証トークン生成
            token = Security.generate_email_verification_token(
                user_id=user_id,
                email=email
            )

            # 現在のサイトURLを取得
            base_url = str(request.base_url).rstrip("/")

            verification_url = (
                f"{base_url}/email/verify"
                f"?token={token}"
            )

            # 認証メール送信
            Mail.send(
                to_email=email,
                subject="【推し活オールインワン】メールアドレス認証",
                html=f"""
                <html>
                <body>
                    <p>推し活オールインワンをご利用いただきありがとうございます。</p>

                    <p>
                        以下のリンクをクリックして、
                        メールアドレスの認証を完了してください。
                    </p>

                    <p>
                        <a href="{verification_url}">
                            メールアドレスを認証する
                        </a>
                    </p>

                    <p>
                        このリンクの有効期限は24時間です。
                    </p>

                    <p>
                        このメールに心当たりがない場合は、
                        このメールを無視してください。
                    </p>

                    <hr>

                    <p>
                        推し活オールインワン
                    </p>
                </body>
                </html>
                """
            )

            # メール送信完了情報をセッションへ保存
            request.session["email_verification_sent_to"] = email

    # =====================================================
    # マイページへ戻る
    # =====================================================

    return RedirectResponse(
        "/mypage",
        status_code=303
    )


def _get_prefecture_groups():
    """
    都道府県一覧をエリアごとにまとめる
    """

    prefecture_list = get_prefecture_list()

    prefecture_groups = OrderedDict()

    for prefecture in prefecture_list:

        area = prefecture["area_name"]

        if area not in prefecture_groups:
            prefecture_groups[area] = []

        prefecture_groups[area].append(prefecture)

    return prefecture_groups


@router.post("/mypage/withdraw")
async def withdraw_mypage(request: Request):
    """退会予約"""

    user_id = request.session.get("user_id")

    # =====================================================
    # ログイン確認
    # =====================================================

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    # =====================================================
    # 現在のユーザー情報取得
    # =====================================================

    user = UserModel.get_user(user_id)

    if not user:
        request.session.clear()

        return RedirectResponse(
            "/login",
            status_code=303
        )

    # =====================================================
    # 通常ユーザー以外は退会対象外
    # =====================================================

    if user["role"] != "user":
        return RedirectResponse(
            "/mypage",
            status_code=303
        )

    # =====================================================
    # 退会予約
    # =====================================================

    success = UserModel.withdraw_user(
        user_id=user_id
    )

    if not success:
        return RedirectResponse(
            "/mypage",
            status_code=303
        )

    # =====================================================
    # 退会予約完了
    # =====================================================

    request.session.clear()

    # トップページ側で表示するメッセージ
    request.session["message"] = (
        "退会予約を受け付けました。"
        "同一アカウントでアクセスすることで、"
        "30日以内は退会を取り消すことができます。"
    )

    return RedirectResponse(
        "/",
        status_code=303
    )
