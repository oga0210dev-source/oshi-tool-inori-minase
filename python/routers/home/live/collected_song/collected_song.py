from fastapi import APIRouter, Request
from python.core import templates

from python.services.collected_song_service import (
    get_song_collection_summary,
    get_collected_song_list,
    get_uncollected_song_list,
    get_live_appearance_song_list
)

router = APIRouter(
    prefix="/home/live/collected_song",
    tags=["home_live_collected_song"]
)


@router.get("")
def collected_song(request: Request):

    user_id = request.session["user_id"]
    summary = get_song_collection_summary(user_id)

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/collected_song/collected_song.html",
        context={
            "request": request,
            "summary": summary
        }
    )


@router.get("/collected")
def collected_song_list(request: Request):

    user_id = request.session["user_id"]
    songs = get_collected_song_list(user_id)

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/collected_song/collected.html",
        context={
            "request": request,
            "songs": songs
        }
    )


@router.get("/uncollected")
def uncollected_song(request: Request):

    user_id = request.session["user_id"]
    songs = get_uncollected_song_list(user_id)

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/collected_song/uncollected.html",
        context={
            "request": request,
            "songs": songs
        }
    )


@router.get("/appearance")
def appearance_song(request: Request):

    songs = get_live_appearance_song_list()

    return templates.TemplateResponse(
        request=request,
        name="templates/home/live/collected_song/appearance.html",
        context={
            "request": request,
            "songs": songs
        }
    )
