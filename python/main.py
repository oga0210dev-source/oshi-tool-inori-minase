import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from python.routers import home, login, register, mypage

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="development-secret-key-change-before-production"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(login.router)
app.include_router(register.router)
app.include_router(mypage.router)

if __name__ == "__main__":
    uvicorn.run(
        "python.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )