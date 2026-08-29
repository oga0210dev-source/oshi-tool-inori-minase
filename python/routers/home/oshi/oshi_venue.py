from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render
from python.models.home.oshi import oshi_venue as oshi_venue_model


router = APIRouter(
    prefix="/home/oshi/venue",
    tags=["home_oshi_venue"]
)


@router.get("")
async def oshi_venue(
        request: Request
):
    keyword = request.query_params.get(
        "keyword",
        ""
    ).strip()

    sort = request.query_params.get(
        "sort",
        "name"
    )

    valid_sorts = {
        "name",
        "prefecture",
        "capacity"
    }

    if sort not in valid_sorts:
        sort = "name"

    venues = oshi_venue_model.get_oshi_venue_list(
        keyword=keyword,
        sort=sort
    )

    return render(
        request=request,
        name="templates/home/oshi/venue.html",
        context={
            "venues": venues,
            "keyword": keyword,
            "sort": sort
        }
    )


@router.get("/{venue_id}/events")
async def oshi_venue_events(
        request: Request,
        venue_id: int
):
    venue = oshi_venue_model.get_oshi_venue(
        venue_id
    )

    if not venue:
        return RedirectResponse(
            "/home/oshi/venue",
            status_code=303
        )

    events = oshi_venue_model.get_oshi_venue_event_list(
        venue_id
    )

    # ツアーごとのキャパ情報
    tour_capacity_map = {}

    # 町民集会ごとのキャパ情報
    meeting_capacity_map = {}

    for event in events:

        if event["event_type"] == "LIVE" and event["tour_name"]:

            tour_name = event["tour_name"]

            if tour_name not in tour_capacity_map:
                tour_capacity_map[tour_name] = (
                    oshi_venue_model.get_oshi_venue_tour_capacity(
                        tour_name
                    )
                )

        elif event["event_type"] == "MEETING" and event["event_name"]:

            meeting_name = event["event_name"]

            if meeting_name not in meeting_capacity_map:
                meeting_capacity_map[meeting_name] = (
                    oshi_venue_model.get_oshi_venue_meeting_capacity(
                        meeting_name
                    )
                )

    return_keyword = request.query_params.get(
        "return_keyword",
        ""
    ).strip()

    return_sort = request.query_params.get(
        "return_sort",
        "name"
    )

    valid_sorts = {
        "name",
        "prefecture",
        "capacity"
    }

    if return_sort not in valid_sorts:
        return_sort = "name"

    return render(
        request=request,
        name="templates/home/oshi/venue_events.html",
        context={
            "venue": venue,
            "events": events,
            "tour_capacity_map": tour_capacity_map,
            "meeting_capacity_map": meeting_capacity_map,
            "return_keyword": return_keyword,
            "return_sort": return_sort
        }
    )
