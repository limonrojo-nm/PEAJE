from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from peaje_core.apis.http.pages import router as pages_router
from peaje_core.apis.http.printer import router as printer_router
from peaje_core.config import get_settings

app = FastAPI(title="peaje-core")

# La app del visitante se sirve desde GitHub Pages (HTTPS, para que anden los
# sensores del teléfono) y peaje-core desde un túnel: son orígenes distintos,
# así que el POST del dibujo necesita CORS. Ver PEAJE_ALLOWED_ORIGINS.
origins = get_settings().allowed_origins_list
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["POST"],
        allow_headers=["*"],
    )

app.include_router(pages_router)
app.include_router(printer_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
