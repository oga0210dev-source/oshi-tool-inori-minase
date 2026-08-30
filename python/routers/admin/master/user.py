from fastapi import APIRouter, Request, Query
from fastapi.responses import RedirectResponse

from python.core import render, auth
from python.models.user import UserModel
from python.utils.date_utils import to_jst


router = APIRouter()


@router.get("/admin/user")
async def user_list(
        request: Request,
        user_name: str = Query(""),
        login_id: str = Query(""),
        role: str = Query(""),
        is_active: str = Query(""),
        withdrawal: str = Query("")
):
    """ユーザー管理"""

    # =====================================================
    # ログイン確認
    # =====================================================

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    # =====================================================
    # 管理者確認
    # =====================================================

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    # =====================================================
    # ユーザー一覧取得
    # =====================================================

    users = UserModel.get_all_users_for_admin(
        user_name=user_name.strip(),
        login_id=login_id.strip(),
        role=role or None,
        is_active=is_active or None,
        withdrawal=withdrawal or None
    )

    return render(
        request=request,
        name="templates/admin/master/user/index.html",
        context={
            "users": users,
            "message": request.query_params.get("message")
        }
    )


@router.post("/admin/user/{user_id}/ban")
async def ban_user(
        request: Request,
        user_id: str
):
    """ユーザーをBAN"""

    # =====================================================
    # ログイン確認
    # =====================================================

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    # =====================================================
    # 管理者確認
    # =====================================================

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    # =====================================================
    # ユーザー取得
    # =====================================================

    user = UserModel.get_user_for_admin(user_id)

    if not user:
        return RedirectResponse(
            "/admin/user?message=ユーザーが存在しません。",
            status_code=303
        )

    # =====================================================
    # BAN
    # =====================================================

    UserModel.set_active(
        user_id=user_id,
        is_active=False
    )

    return RedirectResponse(
        "/admin/user?message=ユーザーをBANしました。",
        status_code=303
    )


@router.post("/admin/user/{user_id}/unban")
async def unban_user(
        request: Request,
        user_id: str
):
    """ユーザーのBANを解除"""

    # =====================================================
    # ログイン確認
    # =====================================================

    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    # =====================================================
    # 管理者確認
    # =====================================================

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    # =====================================================
    # ユーザー取得
    # =====================================================

    user = UserModel.get_user_for_admin(user_id)

    if not user:
        return RedirectResponse(
            "/admin/user?message=ユーザーが存在しません。",
            status_code=303
        )

    # =====================================================
    # BAN解除
    # =====================================================

    UserModel.set_active(
        user_id=user_id,
        is_active=True
    )

    return RedirectResponse(
        "/admin/user?message=ユーザーのBANを解除しました。",
        status_code=303
    )
