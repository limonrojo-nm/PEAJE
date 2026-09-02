"""Lógica de negocio relacionada con la impresora térmica.

Este módulo no sabe nada de HTTP ni de CLI: cualquier capa de API (apis/http,
apis/cli, o una futura tarea de cola) llama a estas funciones.
"""

from datetime import datetime

from peaje_core.printers.client import get_printer
from peaje_core.printers.discovery import UsbPrinterInfo, list_connected_usb_printers


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
        printer.text("Prueba de impresion\n")
        printer.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        printer.cut()
    finally:
        printer.close()
