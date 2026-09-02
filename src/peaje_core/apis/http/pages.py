"""Vistas HTML servidas por peaje-core (panel de pruebas, no la app final del público)."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")
