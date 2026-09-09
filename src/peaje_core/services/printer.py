"""Lógica de negocio relacionada con la impresora térmica.

Este módulo no sabe nada de HTTP ni de CLI: cualquier capa de API (apis/http,
apis/cli, o una futura tarea de cola) llama a estas funciones.
"""

import threading
from datetime import datetime

from PIL import Image

from peaje_core.config import get_settings
from peaje_core.printers.client import get_printer
from peaje_core.printers.imaging import fit_to_width
from peaje_core.printers.discovery import UsbPrinterInfo, list_connected_usb_printers

# Hay una sola impresora y un solo cable. Dos visitantes que terminan a la vez
# llegan por dos threads del pool de FastAPI y abrirían el dispositivo USB en
# paralelo. Serializar acá alcanza mientras haya un solo proceso; cuando haga
# falta escalar, es el punto donde entra la cola de Redis.
_printer_lock = threading.Lock()


def list_connected_printers() -> list[UsbPrinterInfo]:
    """Impresoras USB detectadas físicamente en el host.

    No cubre backends "network"/"serial": esos no se pueden descubrir, solo
    configurar y probar (ver run_print_test).
    """
    return list_connected_usb_printers()


def run_print_test() -> None:
    """Envía un ticket de prueba a la impresora configurada."""
    printer = get_printer()
    try:
        printer.set(align="center", bold=True, width=2, height=2)
        printer.text("PEAJE\n")
        printer.set(align="center", bold=False, width=1, height=1)
        printer.text("Prueba de impresión\n")
        printer.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        # Los acentos del ticket real pasan por acá. python-escpos cambia de
        # página de códigos solo (emite ESC t) para meterlos; si la PP7 numera
        # sus páginas distinto, esta línea sale con glifos equivocados y el
        # resto bien. Es la forma más barata de saberlo: si se lee, andan.
        printer.text("áéíóú ÁÉÍÓÚ ñÑ ¿? ¡!\n")
        printer.cut()
    finally:
        printer.close()


def print_drawing(
    image: Image.Image,
    header: str = "",
    footer: str = "",
) -> None:
    """Imprime el dibujo del visitante como ticket.

    El texto lo pone quien llama: la estación no es la autora del comprobante,
    sólo lo imprime. Al ticket no va ninguna respuesta del visitante — header y
    footer son voz fija de la obra (ver ADR 0005 del repo de la app).
    """
    prepared = fit_to_width(image, get_settings().printer_dots_width)

    with _printer_lock:
        printer = get_printer()
        try:
            if header:
                printer.set(align="center", bold=True)
                printer.text(header.strip() + "\n")
                printer.set(align="center", bold=False)
                printer.text("\n")

            printer.image(prepared)

            if footer:
                # Fuente B: la letra chica del comprobante. A 58 mm entran 42
                # caracteres por renglón contra los 32 de la fuente normal —
                # lo que se pase, la impresora lo parte donde caiga.
                printer.set(align="center", bold=False, font="b")
                printer.text("\n" + footer.strip() + "\n")
                printer.set(font="a")

            printer.text("\n")
            printer.cut()
        finally:
            printer.set(align="left", bold=False)
            printer.close()
