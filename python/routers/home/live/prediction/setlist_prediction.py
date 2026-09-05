from fastapi import APIRouter, Request, Body
from fastapi.responses import RedirectResponse

from python.core import render
from python.core import auth

from python.models.home.live.prediction.setlist_prediction import (
    get_setlist_prediction_list,
    get_setlist_prediction_live_list,
    get_setlist_prediction_live,
    get_setlist_prediction_song_groups,
    get_setlist_prediction,
    get_public_setlist_prediction,
    update_setlist_prediction,
    save_setlist_prediction,
    delete_setlist_prediction
)


router = APIRouter(
    prefix="/home/live/prediction",
    tags=["home_live_prediction"]
)


def login_redirect(request: Request):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    return None


# =========================================================
# セトリ予測入口
# =========================================================

@router.get("")
async def setlist_prediction(
    request: Request
):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    return render(
        request=request,
        name="templates/home/live/prediction/index.html",
        context={}
    )


# =========================================================
# ユーザーセトリ予測一覧
# =========================================================

@router.get("/user")
async def user_setlist_prediction(
    request: Request,
    keyword: str = ""
):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    user_id = request.session.get("user_id")

    predictions = get_setlist_prediction_list(
        user_id,
        keyword if keyword else None
    )

    return render(
        request=request,
        name="templates/home/live/prediction/setlist_prediction.html",
        context={
            "predictions": predictions,
            "keyword": keyword
        }
    )


# =========================================================
# 新規追加：ライブ選択
# =========================================================

@router.get("/new")
async def new_setlist_prediction(
    request: Request
):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    user_id = request.session.get("user_id")

    lives = get_setlist_prediction_live_list(
        user_id
    )

    return render(
        request=request,
        name="templates/home/live/prediction/setlist_prediction_new.html",
        context={
            "lives": lives
        }
    )


# =========================================================
# 新規追加：セトリ予測登録
# =========================================================

@router.get("/new/{live_id}")
async def new_setlist_prediction_live(
    request: Request,
    live_id: int
):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    live = get_setlist_prediction_live(
        live_id
    )

    if not live:
        return RedirectResponse(
            "/home/live/prediction/new",
            status_code=303
        )

    song_groups = get_setlist_prediction_song_groups()

    return render(
        request=request,
        name="templates/home/live/prediction/setlist_prediction_edit.html",
        context={
            "live": live,
            "song_groups": song_groups,
            "songs": [],
            "is_edit": False
        }
    )


# =========================================================
# 新規追加：セトリ予測保存
# =========================================================

@router.post("/new/{live_id}/save")
async def save_prediction(
    request: Request,
    live_id: int,
    songs: list[dict] = Body(...)
):
    if not auth.is_login(request):
        return {
            "success": False,
            "message": "ログインしてください。"
        }

    if not songs:
        return {
            "success": False,
            "message": "予測する曲を追加してください。"
        }

    user_id = request.session.get("user_id")

    prediction_id = save_setlist_prediction(
        user_id,
        live_id,
        songs
    )

    return {
        "success": True,
        "prediction_id": prediction_id,
        "message": "予測セトリを保存しました。"
    }


# =========================================================
# セトリ予測詳細
# =========================================================

@router.get("/detail/{prediction_id}")
async def setlist_prediction_detail(
    request: Request,
    prediction_id: int
):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    user_id = request.session.get("user_id")

    prediction, songs = get_setlist_prediction(
        prediction_id,
        user_id
    )

    if not prediction:
        return RedirectResponse(
            "/home/live/prediction",
            status_code=303
        )

    return render(
        request=request,
        name="templates/home/live/prediction/setlist_prediction_detail.html",
        context={
            "prediction": prediction,
            "songs": songs
        }
    )


# =========================================================
# セトリ予測編集
# =========================================================

@router.get("/edit/{prediction_id}")
async def edit_setlist_prediction(
    request: Request,
    prediction_id: int
):
    redirect = login_redirect(request)

    if redirect:
        return redirect

    user_id = request.session.get("user_id")

    prediction, songs = get_setlist_prediction(
        prediction_id,
        user_id
    )

    if not prediction:
        return RedirectResponse(
            "/home/live/prediction",
            status_code=303
        )

    song_groups = get_setlist_prediction_song_groups()

    return render(
        request=request,
        name="templates/home/live/prediction/setlist_prediction_edit.html",
        context={
            "live": prediction,
            "prediction": prediction,
            "songs": songs,
            "song_groups": song_groups,
            "is_edit": True
        }
    )


# =========================================================
# セトリ予測更新
# =========================================================

@router.post("/{prediction_id}/save")
async def save_edited_prediction(
    request: Request,
    prediction_id: int,
    songs: list[dict] = Body(...)
):
    if not auth.is_login(request):
        return {
            "success": False,
            "message": "ログインしてください。"
        }

    if not songs:
        return {
            "success": False,
            "message": "予測する曲を追加してください。"
        }

    user_id = request.session.get("user_id")

    success = update_setlist_prediction(
        prediction_id,
        user_id,
        songs
    )

    if not success:
        return {
            "success": False,
            "message": "予測セトリの更新に失敗しました。"
        }

    return {
        "success": True,
        "message": "予測セトリを更新しました。"
    }


# =========================================================
# セトリ予測削除
# =========================================================

@router.post("/{prediction_id}/delete")
async def delete_prediction(
    request: Request,
    prediction_id: int
):
    if not auth.is_login(request):
        return {
            "success": False,
            "message": "ログインしてください。"
        }

    user_id = request.session.get("user_id")

    success = delete_setlist_prediction(
        prediction_id,
        user_id
    )

    if not success:
        return {
            "success": False,
            "message": "予測セトリの削除に失敗しました。"
        }

    return {
        "success": True,
        "message": "予測セトリを削除しました。"
    }


# =========================================================
# セトリ予測共有ページ
# ※ ログイン不要
# =========================================================

@router.get("/share/{prediction_id}")
async def share_setlist_prediction(
    request: Request,
    prediction_id: int
):
    prediction, songs = get_public_setlist_prediction(
        prediction_id
    )

    if not prediction:
        return render(
            request=request,
            name="templates/home/live/prediction/setlist_prediction_share.html",
            context={
                "prediction": None,
                "songs": [],
                "not_found": True
            }
        )

    return render(
        request=request,
        name="templates/home/live/prediction/setlist_prediction_share.html",
        context={
            "prediction": prediction,
            "songs": songs,
            "not_found": False
        }
    )
