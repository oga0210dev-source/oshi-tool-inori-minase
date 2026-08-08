from fastapi import FastAPI

from python.routers import login, register
from python.routers.home import home
from python.routers.home.live import setlist as live_setlist, live, detail as live_detail
from python.routers.home.live.archive import archive
from python.routers.home.live.history import (history, history_detail, history_edit, history_expense_add,
                                              history_expense_edit,history_expense_delete)
from python.routers.home.live.collected_song import collected_song
from python.routers.mypage import mypage, password, public_setting
from python.routers.admin.master import master, song as song_master, live as live_master, setlist as setlist_master


def register_router(app: FastAPI):

    app.include_router(home.router)
    app.include_router(login.router)
    app.include_router(register.router)

    app.include_router(mypage.router)
    app.include_router(password.router)
    app.include_router(public_setting.router)

    app.include_router(master.router)
    app.include_router(song_master.router)
    app.include_router(live_master.router)
    app.include_router(setlist_master.router)

    app.include_router(live.router)
    app.include_router(archive.router)
    app.include_router(live_detail.router)
    app.include_router(live_setlist.router)
    app.include_router(history.router)
    app.include_router(history_detail.router)
    app.include_router(history_edit.router)
    app.include_router(history_expense_add.router)
    app.include_router(history_expense_delete.router)
    app.include_router(history_expense_edit.router)
    app.include_router(collected_song.router)
