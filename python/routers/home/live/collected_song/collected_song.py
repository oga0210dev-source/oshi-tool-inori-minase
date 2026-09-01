from fastapi import APIRouter, Request

from python.core import render

from python.services.collected_song_service import (
    get_song_collection_summary,
    get_collected_song_list,
    get_uncollected_song_list,
    get_live_appearance_song_list,
    get_live_appearance_song_detail
)


router = APIRouter(
    prefix="/home/live/collected_song",
    tags=["home_live_collected_song"]
)


@router.get("")
def collected_song(request: Request):

    user_id = request.session["user_id"]

    summary = get_song_collection_summary(
        user_id,
        mode="live"
    )

    summary_with_chomin = get_song_collection_summary(
        user_id,
        mode="chomin"
    )

    summary_all_meeting_songs = get_song_collection_summary(
        user_id,
        mode="all"
    )

    return render(
        request=request,
        name="templates/home/live/collected_song/collected_song.html",
        context={
            "request": request,
            "summary": summary,
            "summary_with_chomin": summary_with_chomin,
            "summary_all_meeting_songs": summary_all_meeting_songs
        }
    )


@router.get("/collected")
def collected_song_list(
        request: Request,
        mode: str = "live"
):

    user_id = request.session["user_id"]

    if mode not in ("live", "chomin", "all"):
        mode = "live"

    songs = get_collected_song_list(
        user_id,
        mode=mode
    )

    return render(
        request=request,
        name="templates/home/live/collected_song/collected.html",
        context={
            "request": request,
            "songs": songs,
            "mode": mode
        }
    )


@router.get("/uncollected")
def uncollected_song(
        request: Request,
        mode: str = "live"
):

    user_id = request.session["user_id"]

    if mode not in ("live", "chomin", "all"):
        mode = "live"

    songs = get_uncollected_song_list(
        user_id,
        mode=mode
    )

    return render(
        request=request,
        name="templates/home/live/collected_song/uncollected.html",
        context={
            "request": request,
            "songs": songs,
            "mode": mode
        }
    )


@router.get("/appearance")
def appearance_song(
        request: Request,
        mode: str = "live"
):

    if mode not in ("live", "chomin", "all"):
        mode = "live"

    songs = get_live_appearance_song_list(
        mode=mode
    )

    return render(
        request=request,
        name="templates/home/live/collected_song/appearance.html",
        context={
            "request": request,
            "songs": songs,
            "mode": mode
        }
    )


@router.get("/appearance/{song_group_id}")
def appearance_song_detail(
        request: Request,
        song_group_id: int,
        mode: str = "live",
        from_: str = "appearance"
):

    if mode not in ("live", "chomin", "all"):
        mode = "live"

    if from_ not in ("collected", "appearance"):
        from_ = "appearance"

    song = get_live_appearance_song_detail(
        song_group_id=song_group_id,
        mode=mode
    )

    if not song:
        return render(
            request=request,
            name="templates/home/live/collected_song/appearance_detail.html",
            context={
                "request": request,
                "song": None,
                "mode": mode,
                "from_": from_
            }
        )

    return render(
        request=request,
        name="templates/home/live/collected_song/appearance_detail.html",
        context={
            "request": request,
            "song": song,
            "mode": mode,
            "from_": from_
        }
    )
