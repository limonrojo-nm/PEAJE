"""Fábrica del cliente ESC/POS: traduce la configuración (config.Settings) al
backend de conexión correspondiente de python-escpos.

Uso real (Aclas PP7): backend "usb" o "serial" en la Raspberry Pi.
Uso en desarrollo: backend "network" apuntando al simulador escpresso.
"""

from escpos.escpos import Escpos
from escpos.printer import Dummy, Network, Serial, Usb

from peaje_core.config import Settings, get_settings


def get_printer(settings: Settings | None = None) -> Escpos:
    settings = settings or get_settings()

    if settings.printer_backend == "network":
        return Network(settings.printer_host, port=settings.printer_port)

    if settings.printer_backend == "usb":
        if settings.printer_usb_vendor_id is None or settings.printer_usb_product_id is None:
            raise ValueError(
                "Backend 'usb' requiere PEAJE_PRINTER_USB_VENDOR_ID y "
                "PEAJE_PRINTER_USB_PRODUCT_ID."
            )
        return Usb(
            settings.printer_usb_vendor_id,
            settings.printer_usb_product_id,
            in_ep=settings.printer_usb_in_ep,
            out_ep=settings.printer_usb_out_ep,
        )

    if settings.printer_backend == "serial":
        return Serial(
            devfile=settings.printer_serial_devfile,
            baudrate=settings.printer_serial_baudrate,
        )

    if settings.printer_backend == "dummy":
        return Dummy()

    raise ValueError(f"Backend de impresora desconocido: {settings.printer_backend!r}")
