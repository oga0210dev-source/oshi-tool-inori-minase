from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render
from python.core import auth
from python.models.home.live.lost_item import lost_item as lost_item_model


router = APIRouter(
    prefix="/home/live/lost-item",
    tags=["home_live_lost_item"]
)


def login_redirect(request: Request):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    return None


# =========================================================
# 忘れ物チェック
# =========================================================

@router.get("")
async def lost_item_list(request: Request):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    user_id = request.session.get("user_id")

    # 初回アクセス時のみデフォルト項目を作成
    lost_item_model.initialize_lost_items(user_id)

    items = lost_item_model.get_lost_item_list(user_id)

    return render(
        request=request,
        name="templates/home/live/lost_item/lost_item.html",
        context={
            "items": items
        }
    )


# =========================================================
# チェック状態更新
# =========================================================

@router.post("/check")
async def update_check(
    request: Request
):
    if not auth.is_login(request):
        return {
            "success": False,
            "message": "ログインしてください。"
        }

    data = await request.json()

    user_id = request.session.get("user_id")

    lost_item_model.update_lost_item_check(
        user_id,
        data["user_lost_item_id"],
        data["is_checked"]
    )

    return {
        "success": True
    }


# =========================================================
# 個人項目追加
# =========================================================

@router.post("/add")
async def add_item(
    request: Request
):
    if not auth.is_login(request):
        return {
            "success": False,
            "message": "ログインしてください。"
        }

    data = await request.json()

    item_name = data.get("item_name", "").strip()

    if not item_name:
        return {
            "success": False,
            "message": "項目名を入力してください。"
        }

    if len(item_name) > 100:
        return {
            "success": False,
            "message": "項目名は100文字以内で入力してください。"
        }

    user_id = request.session.get("user_id")

    user_lost_item_id = lost_item_model.add_lost_item(
        user_id,
        item_name
    )

    return {
        "success": True,
        "user_lost_item_id": user_lost_item_id,
        "message": "項目を追加しました。"
    }


# =========================================================
# 個人項目編集
# =========================================================

@router.post("/update")
async def update_item(
    request: Request
):
    if not auth.is_login(request):
        return {
            "success": False,
            "message": "ログインしてください。"
        }

    data = await request.json()

    item_name = data.get("item_name", "").strip()

    if not item_name:
        return {
            "success": False,
            "message": "項目名を入力してください。"
        }

    if len(item_name) > 100:
        return {
            "success": False,
            "message": "項目名は100文字以内で入力してください。"
        }

    user_id = request.session.get("user_id")

    lost_item_model.update_lost_item(
        user_id,
        data["user_lost_item_id"],
        item_name
    )

    return {
        "success": True,
        "message": "項目を更新しました。"
    }


# =========================================================
# 個人項目削除
# =========================================================

@router.post("/delete")
async def delete_item(
    request: Request
):
    if not auth.is_login(request):
        return {
            "success": False,
            "message": "ログインしてください。"
        }

    data = await request.json()

    user_id = request.session.get("user_id")

    lost_item_model.delete_lost_item(
        user_id,
        data["user_lost_item_id"]
    )

    return {
        "success": True,
        "message": "項目を削除しました。"
    }


# =========================================================
# リセット
# =========================================================

@router.post("/reset")
async def reset_items(
    request: Request
):
    if not auth.is_login(request):
        return {
            "success": False,
            "message": "ログインしてください。"
        }

    user_id = request.session.get("user_id")

    lost_item_model.reset_lost_items(user_id)

    return {
        "success": True,
        "message": "チェック状態をリセットしました。"
    }
