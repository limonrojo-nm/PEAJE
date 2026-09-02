"""Capa HTTP para las operaciones de impresora: solo traduce request/response,
la lógica vive en services.printer.
"""

from fastapi import APIRouter, HTTPException

from peaje_core.printers.discovery import UsbPrinterInfo, UsbDiscoveryUnavailable
from peaje_core.services.printer import list_connected_printers, run_print_test

router = APIRouter(prefix="/printer", tags=["printer"])


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
