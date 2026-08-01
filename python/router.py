from fastapi import FastAPI

from python.routers import home, login, register
from python.routers.mypage import mypage, password, public_setting
from python.routers.admin.master import master, song, live


def register_router(app: FastAPI):

    app.include_router(home.router)
    app.include_router(login.router)
    app.include_router(register.router)

    app.include_router(mypage.router)
    app.include_router(password.router)
    app.include_router(public_setting.router)

    app.include_router(master.router)
    app.include_router(song.router)
    app.include_router(live.router)
