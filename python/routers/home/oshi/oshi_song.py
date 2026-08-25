from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render
from python.models.home.oshi import oshi_song as song_model
from python.utils import util


router = APIRouter(
    prefix="/home/oshi/song",
    tags=["home_oshi_song"]
)


@router.get("")
async def song_list(
        request: Request,
        keyword: str = None,
        sort: str = "album"
):
    songs = song_model.get_song_list(
        keyword,
        sort
    )

    albums = util.group_by_album(songs)

    return render(
        request=request,
        name="templates/home/oshi/song.html",
        context={
            "albums": albums,
            "keyword": keyword,
            "sort": sort
        }
    )
