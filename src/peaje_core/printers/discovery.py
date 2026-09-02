"""Descubrimiento de impresoras USB conectadas al host.

Capa de infraestructura: habla directo con pyusb. services.printer expone
esto al resto de la app sin que le importen los detalles de USB.
"""

from typing import TypedDict

try:
    import usb.core
    import usb.util

    _USB_AVAILABLE = True
except ImportError:
    _USB_AVAILABLE = False

# USB Device Class Code para impresoras (usb.org Base Class 7h).
_PRINTER_CLASS = 0x07


class UsbPrinterInfo(TypedDict):
    vendor_id: str
    product_id: str
    manufacturer: str | None
    product: str | None


class UsbDiscoveryUnavailable(RuntimeError):
    """No se puede enumerar dispositivos USB en este sistema."""


def list_connected_usb_printers() -> list[UsbPrinterInfo]:
    """Enumera los dispositivos USB conectados que se anuncian como impresora.

    Requiere pyusb y su backend nativo (libusb). En macOS: `brew install libusb`.
    """
    if not _USB_AVAILABLE:
        raise UsbDiscoveryUnavailable(
            "pyusb no está instalado (extra 'usb' de python-escpos)."
        )

    try:
        devices = list(usb.core.find(find_all=True))
    except usb.core.NoBackendError as exc:
        raise UsbDiscoveryUnavailable(
            "No se encontró un backend USB nativo (libusb). "
            "En macOS: 'brew install libusb'. En Raspberry Pi OS/Debian: "
            "'sudo apt install libusb-1.0-0'."
        ) from exc

    return [_describe(device) for device in devices if _is_printer_class(device)]


def _is_printer_class(device: "usb.core.Device") -> bool:
    if device.bDeviceClass == _PRINTER_CLASS:
        return True
    try:
        return any(
            interface.bInterfaceClass == _PRINTER_CLASS
            for configuration in device
            for interface in configuration
        )
    except (usb.core.USBError, NotImplementedError):
        return False


def _describe(device: "usb.core.Device") -> UsbPrinterInfo:
    return {
        "vendor_id": hex(device.idVendor),
        "product_id": hex(device.idProduct),
        "manufacturer": _safe_string(device, device.iManufacturer),
        "product": _safe_string(device, device.iProduct),
    }


def _safe_string(device: "usb.core.Device", index: int) -> str | None:
    if not index:
        return None
    try:
        return usb.util.get_string(device, index)
    except (usb.core.USBError, ValueError):
        return None
