from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de peaje-core, sobreescribible por variables de entorno PEAJE_*."""

    model_config = SettingsConfigDict(env_prefix="PEAJE_")

    printer_backend: Literal["network", "usb", "serial", "dummy"] = "network"

    # backend "network": conexión a la impresora real por LAN/WiFi, o al
    # simulador escpresso corriendo en localhost durante desarrollo.
    printer_host: str = "127.0.0.1"
    printer_port: int = 9100

    # backend "usb": Aclas PP7 conectada por cable a la Raspberry Pi.
    printer_usb_vendor_id: int | None = None
    printer_usb_product_id: int | None = None

    # backend "serial": conexión serie directa.
    printer_serial_devfile: str = "/dev/serial0"
    printer_serial_baudrate: int = 19200


@lru_cache
def get_settings() -> Settings:
    return Settings()
