"""Capa HTTP para las operaciones de impresora: solo traduce request/response,
la lógica vive en services.printer.
"""

import io

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image, UnidentifiedImageError

from peaje_core.printers.discovery import UsbPrinterInfo, UsbDiscoveryUnavailable
from peaje_core.services.printer import (
    list_connected_printers,
    print_drawing,
    run_print_test,
)

router = APIRouter(prefix="/printer", tags=["printer"])

# El dibujo es un PNG de un canvas de celular: ~200 KB. El tope está para que
# un POST cualquiera no se coma la memoria de la Raspberry.
MAX_DRAWING_BYTES = 5 * 1024 * 1024

# El texto del ticket lo manda la obra. Un tope para que nadie use la impresora
# de la sala como salida de texto arbitrario.
MAX_TEXT_CHARS = 500


@router.get("/connected")
def connected() -> dict[str, list[UsbPrinterInfo]]:
    try:
        printers = list_connected_printers()
    except UsbDiscoveryUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"usb_printers": printers}


@router.post("/test-print")
def test_print() -> dict[str, str]:
    try:
        run_print_test()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al imprimir: {exc}") from exc
    return {"status": "ok"}


@router.post("/drawing")
async def drawing(
    drawing: UploadFile = File(...),
    header: str = Form(""),
    footer: str = Form(""),
) -> dict[str, str]:
    """Recibe el dibujo del visitante y lo imprime como ticket.

    Lo manda la app al llegar al final del recorrido. `header` y `footer` son
    la voz de la obra —fijos, iguales en cada ticket—: la estación no decide
    qué dice el comprobante. No llega ningún dato del visitante.
    """
    if len(header) > MAX_TEXT_CHARS or len(footer) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=413, detail="Texto del ticket demasiado largo.")

    raw = await drawing.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Dibujo vacío.")
    if len(raw) > MAX_DRAWING_BYTES:
        raise HTTPException(status_code=413, detail="Dibujo demasiado grande.")

    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail=f"No es una imagen: {exc}") from exc

    # print_drawing es bloqueante (USB): fuera del event loop.
    try:
        await run_in_threadpool(print_drawing, image, header, footer)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al imprimir: {exc}") from exc

    return {"status": "ok"}
