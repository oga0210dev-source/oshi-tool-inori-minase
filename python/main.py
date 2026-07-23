import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from python.database.user_table import create_tables
from starlette.middleware.sessions import SessionMiddleware

from python.routers import home, login, register

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="development-secret-key-change-before-production"
)

create_tables()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(login.router)
app.include_router(register.router)

if __name__ == "__main__":
    uvicorn.run(
        "python.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )