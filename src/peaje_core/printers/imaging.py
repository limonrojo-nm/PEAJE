"""Preparación de imágenes para la impresora térmica.

Capa de infraestructura: acá vive todo lo que tiene que ver con el papel.
python-escpos convierte a 1 bit por su cuenta (gris → invertido → dithering
Floyd–Steinberg), pero **no reescala**: si la imagen es más ancha que el
cabezal, se corta. Ese reescalado es lo que hace este módulo.
"""

from PIL import Image


def fit_to_width(image: Image.Image, dots: int) -> Image.Image:
    """Lleva la imagen al ancho exacto del cabezal, manteniendo la proporción.

    :param dots: ancho de la impresora en puntos (ver Settings.printer_dots_width)
    """
    if image.width == dots:
        return image
    height = max(1, round(image.height * dots / image.width))
    return image.resize((dots, height), Image.LANCZOS)
