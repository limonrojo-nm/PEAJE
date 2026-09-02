from fastapi import FastAPI

from peaje_core.apis.http.pages import router as pages_router
from peaje_core.apis.http.printer import router as printer_router

app = FastAPI(title="peaje-core")

app.include_router(pages_router)
app.include_router(printer_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
