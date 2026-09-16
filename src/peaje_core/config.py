from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de peaje-core, sobreescribible por variables de entorno PEAJE_*."""

    # Además del entorno, lee un .env en la carpeta desde donde se corre (ver
    # .env.example): así la configuración de la Raspberry vive en un archivo y
    # no en exports que se pierden al cerrar la terminal o reiniciar. Una
    # variable de entorno con el mismo nombre pisa al archivo.
    model_config = SettingsConfigDict(
        env_prefix="PEAJE_", env_file=".env", env_file_encoding="utf-8"
    )

    printer_backend: Literal["network", "usb", "serial", "dummy"] = "network"

    # backend "network": conexión a la impresora real por LAN/WiFi, o al
    # simulador escpresso corriendo en localhost durante desarrollo.
    printer_host: str = "127.0.0.1"
    printer_port: int = 9100

    # backend "usb": Aclas PP7 conectada por cable a la Raspberry Pi (o, en
    # desarrollo, directo a la Mac). Los endpoints in/out por defecto son los
    # que expone la Aclas PP7 (confirmados con pyusb: interfaz Printer, bulk
    # OUT 0x03 / bulk IN 0x81) — python-escpos por defecto asume 0x81/0x01,
    # que no corresponde con este dispositivo.
    printer_usb_vendor_id: int | None = None
    printer_usb_product_id: int | None = None
    printer_usb_in_ep: int = 0x81
    printer_usb_out_ep: int = 0x03

    @field_validator(
        "printer_usb_vendor_id",
        "printer_usb_product_id",
        "printer_usb_in_ep",
        "printer_usb_out_ep",
        mode="before",
    )
    @classmethod
    def _int_decimal_o_hexa(cls, value: object) -> object:
        # lsusb muestra los IDs en hexa ("0483:5840"); pydantic sólo entiende
        # decimal. Aceptar "0x0483" y "1155" por igual.
        if isinstance(value, str):
            return int(value.strip(), 0)
        return value

    # Ancho del cabezal en puntos. 58 mm ≈ 384, 80 mm ≈ 576. Confirmar contra
    # el manual de la Aclas PP7: el dibujo se reescala a esta medida y si no
    # coincide, sale cortado o angosto.
    printer_dots_width: int = 384

    # Comando ESC/POS con el que se manda el dibujo. python-escpos ofrece tres:
    #   bitImageColumn  ESC *      el más viejo; lo entienden hasta las básicas
    #   bitImageRaster  GS v 0     el habitual en Epson y clones
    #   graphics        GS ( L     el moderno
    # La Aclas PP7 rechaza GS v 0 —imprime "(1B 80) This command is not
    # supported" y se apaga a mitad del dibujo—, así que el default es columna.
    # Para probar un modo contra la impresora: `peaje-core printer image-test`.
    printer_image_impl: Literal["bitImageColumn", "bitImageRaster", "graphics"] = (
        "bitImageColumn"
    )

    # Orígenes que pueden mandar un dibujo (CORS). La app se sirve desde
    # GitHub Pages y peaje-core desde un túnel HTTPS, así que son orígenes
    # distintos. Coma como separador:
    #   PEAJE_ALLOWED_ORIGINS=https://usuario.github.io
    allowed_origins: str = ""

    # backend "serial": conexión serie directa.
    printer_serial_devfile: str = "/dev/serial0"
    printer_serial_baudrate: int = 19200


    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
