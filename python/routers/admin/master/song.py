from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import templates
from python.core import auth

from python.models.admin.master import song as song_model
from python.utils import validator, util


router = APIRouter(
    prefix="/admin/master/song",
    tags=["admin_master_song"]
)


@router.get("")
async def song_list(
        request: Request,
        keyword: str = None,
        sort: str = "album"
):
    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    songs = song_model.get_song_list(
        keyword,
        sort
    )

    albums = util.group_by_album(songs)

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/song/index.html",
        context={
            "albums": albums,
            "keyword": keyword,
            "sort": sort
        }
    )


@router.get("/group/{song_group_id}")
async def song_group_get(
        request: Request,
        song_group_id: int
):
    if not auth.is_login(request):
        return {"error": "login"}

    if not auth.is_admin(request):
        return {"error": "permission"}

    song = song_model.get_song_by_group(song_group_id)

    return song


@router.get("/create")
async def song_create_page(request: Request):
    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    # 管理者確認
    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    song_groups = song_model.get_song_groups()

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/song/form.html",
        context={
            "song": None,
            "song_groups": song_groups
        }
    )


@router.post("/create")
async def song_create(
        request: Request,

        song_name: str = Form(...),
        song_type: str = Form("INORI"),
        song_group_id: int = Form(None),
        release_date: str = Form(None),
        album_name: str = Form(None),
        display_order: int = Form(None),
        lyricist: str = Form(None),
        composer: str = Form(None),
        arranger: str = Form(None),
        tie_up: str = Form(None),
        youtube_url: str = Form(None),
        apple_music_url: str = Form(None),
        spotify_url: str = Form(None),
        is_public: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    song_data = {
        "song_name": song_name,
        "song_type": song_type,
        "song_group_id": song_group_id,
        "release_date": release_date,
        "album_name": album_name,
        "display_order": display_order,
        "lyricist": lyricist,
        "composer": composer,
        "arranger": arranger,
        "tie_up": tie_up,
        "youtube_url": youtube_url,
        "apple_music_url": apple_music_url,
        "spotify_url": spotify_url,
        "is_public": is_public
    }

    song_groups = song_model.get_song_groups()

    if not song_name.strip():
        return templates.TemplateResponse(
            request=request,
            name="templates/admin/master/song/form.html",
            context={
                "error": "曲名を入力してください",
                "song": song_data,
                "song_groups": song_groups
            }
        )

    if song_type not in ("INORI", "OTHER"):
        return templates.TemplateResponse(
            request=request,
            name="templates/admin/master/song/form.html",
            context={
                "error": "曲タイプが不正です",
                "song": song_data,
                "song_groups": song_groups
            }
        )

    if song_model.exists_song(
            song_name,
            album_name
    ):
        return templates.TemplateResponse(
            request=request,
            name="templates/admin/master/song/form.html",
            context={
                "error": "同じアルバムに同じ曲名が登録されています",
                "song": song_data,
                "song_groups": song_groups
            }
        )

    if display_order is not None and display_order < 1:
        return templates.TemplateResponse(
            request=request,
            name="templates/admin/master/song/form.html",
            context={
                "error": "表示順は1以上で入力してください",
                "song": song_data,
                "song_groups": song_groups
            }
        )

    url_list = [
        ("YouTube URL", youtube_url),
        ("Apple Music URL", apple_music_url),
        ("Spotify URL", spotify_url)
    ]

    for name, url in url_list:
        if not validator.is_valid_url(url):
            return templates.TemplateResponse(
                request=request,
                name="templates/admin/master/song/form.html",
                context={
                    "error": f"{name}の形式が正しくありません",
                    "song": song_data,
                    "song_groups": song_groups
                }
            )

    song_model.create_song(song_data)

    return RedirectResponse(
        "/admin/master/song",
        status_code=303
    )


@router.get("/edit/{song_id}")
async def song_edit_page(
        request: Request,
        song_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    song = song_model.get_song(song_id)
    song_groups = song_model.get_song_groups()

    return templates.TemplateResponse(
        request=request,
        name="templates/admin/master/song/form.html",
        context={
            "song": song,
            "song_groups": song_groups
        }
    )


@router.post("/update/{song_id}")
async def song_update(
        request: Request,
        song_id: int,

        song_name: str = Form(...),
        song_type: str = Form("INORI"),
        song_group_id: int = Form(None),
        release_date: str = Form(None),
        album_name: str = Form(None),
        display_order: int = Form(None),
        lyricist: str = Form(None),
        composer: str = Form(None),
        arranger: str = Form(None),
        tie_up: str = Form(None),
        youtube_url: str = Form(None),
        apple_music_url: str = Form(None),
        spotify_url: str = Form(None),
        is_public: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    song_data = {
        "song_name": song_name,
        "song_type": song_type,
        "song_group_id": song_group_id,
        "release_date": release_date,
        "album_name": album_name,
        "display_order": display_order,
        "lyricist": lyricist,
        "composer": composer,
        "arranger": arranger,
        "tie_up": tie_up,
        "youtube_url": youtube_url,
        "apple_music_url": apple_music_url,
        "spotify_url": spotify_url,
        "is_public": is_public
    }

    song_groups = song_model.get_song_groups()

    if not song_name.strip():
        return templates.TemplateResponse(
            request=request,
            name="templates/admin/master/song/form.html",
            context={
                "error": "曲名を入力してください",
                "song": song_data,
                "song_groups": song_groups
            }
        )

    if song_type not in ("INORI", "OTHER"):
        return templates.TemplateResponse(
            request=request,
            name="templates/admin/master/song/form.html",
            context={
                "error": "曲タイプが不正です",
                "song": song_data,
                "song_groups": song_groups
            }
        )

    if not song_group_id:
        song = song_model.get_song(song_id)
        song_data["song_group_id"] = song["song_group_id"]

    if song_model.exists_song(
            song_name,
            album_name,
            song_id
    ):
        return templates.TemplateResponse(
            request=request,
            name="templates/admin/master/song/form.html",
            context={
                "error": "同じアルバムに同じ曲名が登録されています",
                "song": song_data,
                "song_groups": song_groups
            }
        )

    if display_order is not None and display_order < 1:
        return templates.TemplateResponse(
            request=request,
            name="templates/admin/master/song/form.html",
            context={
                "error": "表示順は1以上で入力してください",
                "song": song_data,
                "song_groups": song_groups
            }
        )

    url_list = [
        ("YouTube URL", youtube_url),
        ("Apple Music URL", apple_music_url),
        ("Spotify URL", spotify_url)
    ]

    for name, url in url_list:
        if not validator.is_valid_url(url):
            return templates.TemplateResponse(
                request=request,
                name="templates/admin/master/song/form.html",
                context={
                    "error": f"{name}の形式が正しくありません",
                    "song": song_data,
                    "song_groups": song_groups
                }
            )

    song_model.update_song(
        song_id,
        song_data
    )

    return RedirectResponse(
        "/admin/master/song",
        status_code=303
    )


@router.get("/delete/{song_id}")
async def song_delete(
        request: Request,
        song_id: int
):
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    if not auth.is_admin(request):
        return RedirectResponse("/home", status_code=303)

    song_model.delete_song(song_id)

    return RedirectResponse(
        "/admin/master/song",
        status_code=303
    )
