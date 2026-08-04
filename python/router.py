from fastapi import FastAPI

from python.routers import login, register
from python.routers.home import home
from python.routers.home import live
from python.routers.mypage import mypage, password, public_setting
from python.routers.admin.master import master, song as song_master, live as live_master, setlist


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
    app.include_router(setlist.router)

    app.include_router(live.router)
