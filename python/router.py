from fastapi import FastAPI

from python.routers import (
    login,
    register,
    batch,
    font,
    user_setting,
    email
)
from python.routers.home import (
    home,
    legal,
    inquiry as home_inquiry,
    announcement
)
from python.routers.home.live import (
    live,
    detail as live_detail,
    setlist as live_setlist
)
from python.routers.home.live.archive import archive as live_archive
from python.routers.home.live.history import (
    history as live_history,
    history_detail as live_history_detail,
    history_edit as live_history_edit,
    history_expense_add as live_history_expense_add,
    history_expense_edit as live_history_expense_edit,
    history_expense_delete as live_history_expense_delete
)
from python.routers.home.live.lost_item import lost_item
from python.routers.home.live.prediction import setlist_prediction
from python.routers.home.live.collected_song import collected_song
from python.routers.home.meeting import (
    meeting,
    detail as meeting_detail,
    setlist as meeting_setlist
)
from python.routers.home.meeting.archive import archive as meeting_archive
from python.routers.home.meeting.history import (
    history as meeting_history,
    history_detail as meeting_history_detail,
    history_edit as meeting_history_edit,
    history_expense_add as meeting_history_expense_add,
    history_expense_edit as meeting_history_expense_edit,
    history_expense_delete as meeting_history_expense_delete
)
from python.routers.home.meeting.guest import (
    guest as meeting_guest,
    detail as meeting_guest_detail
)
from python.routers.home.oshi import (
    oshi,
    oshi_work,
    oshi_anniversary,
    oshi_official_link,
    oshi_song,
    oshi_program,
    oshi_venue
)
from python.routers.mypage import mypage, password, public_setting
from python.routers.admin.master import (
    master,
    announcement as master_announcement,
    song as song_master,
    venue as venue_master,
    live as live_master,
    meeting as meeting_master,
    setlist as setlist_master,
    oshi as oshi_master,
    oshi_work as oshi_work_master,
    oshi_anniversary as oshi_anniversary_master,
    oshi_official_link as oshi_official_link_master,
    oshi_program as oshi_program_master,
    user as user_master,
    access as access_master
)
from python.routers.admin import inquiry as admin_inquiry


def register_router(app: FastAPI):

    app.include_router(home.router)
    app.include_router(legal.router)
    app.include_router(home_inquiry.router)
    app.include_router(login.router)
    app.include_router(register.router)
    app.include_router(font.router)
    app.include_router(user_setting.router)
    app.include_router(email.router)
    app.include_router(announcement.router)

    app.include_router(batch.router)

    app.include_router(mypage.router)
    app.include_router(password.router)
    app.include_router(public_setting.router)

    app.include_router(admin_inquiry.router)

    app.include_router(master.router)
    app.include_router(master_announcement.router)
    app.include_router(song_master.router)
    app.include_router(venue_master.router)
    app.include_router(live_master.router)
    app.include_router(meeting_master.router)
    app.include_router(setlist_master.router)
    app.include_router(oshi_master.router)
    app.include_router(oshi_work_master.router)
    app.include_router(oshi_anniversary_master.router)
    app.include_router(oshi_official_link_master.router)
    app.include_router(oshi_program_master.router)
    app.include_router(user_master.router)
    app.include_router(access_master.router)

    app.include_router(live.router)
    app.include_router(live_archive.router)
    app.include_router(live_detail.router)
    app.include_router(live_setlist.router)
    app.include_router(live_history.router)
    app.include_router(live_history_detail.router)
    app.include_router(live_history_edit.router)
    app.include_router(live_history_expense_add.router)
    app.include_router(live_history_expense_delete.router)
    app.include_router(live_history_expense_edit.router)
    app.include_router(collected_song.router)
    app.include_router(setlist_prediction.router)
    app.include_router(lost_item.router)

    app.include_router(meeting.router)
    app.include_router(meeting_archive.router)
    app.include_router(meeting_detail.router)
    app.include_router(meeting_setlist.router)
    app.include_router(meeting_history.router)
    app.include_router(meeting_history_detail.router)
    app.include_router(meeting_history_edit.router)
    app.include_router(meeting_history_expense_add.router)
    app.include_router(meeting_history_expense_edit.router)
    app.include_router(meeting_history_expense_delete.router)
    app.include_router(meeting_guest.router)
    app.include_router(meeting_guest_detail.router)

    app.include_router(oshi.router)
    app.include_router(oshi_work.router)
    app.include_router(oshi_anniversary.router)
    app.include_router(oshi_official_link.router)
    app.include_router(oshi_song.router)
    app.include_router(oshi_program.router)
    app.include_router(oshi_venue.router)
