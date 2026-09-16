"""Capa de comandos de terminal para operaciones de impresora: solo traduce
argumentos/salida de consola, la lógica vive en services.printer.
"""

import typer

from peaje_core.services.printer import run_image_test, run_print_test

app = typer.Typer(help="Comandos relacionados con la impresora térmica")


@app.command("test")
def test() -> None:
    """Ejecuta una impresión de prueba."""
    run_print_test()
    typer.echo("Impresión de prueba enviada.")


@app.command("image-test")
def image_test(
    impl: str | None = typer.Option(
        None,
        help="Modo de imagen a probar: bitImageColumn, bitImageRaster o graphics. "
        "Sin esto usa PEAJE_PRINTER_IMAGE_IMPL.",
    ),
) -> None:
    """Imprime una figura de prueba para ver qué comando de imagen entiende la impresora."""
    used = run_image_test(impl)
    typer.echo(f"Imagen de prueba enviada con el modo {used}.")
