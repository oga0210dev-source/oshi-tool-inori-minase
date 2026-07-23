from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from python.core import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )