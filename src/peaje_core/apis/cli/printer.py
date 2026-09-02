"""Capa de comandos de terminal para operaciones de impresora: solo traduce
argumentos/salida de consola, la lógica vive en services.printer.
"""

import typer

from peaje_core.services.printer import run_print_test

app = typer.Typer(help="Comandos relacionados con la impresora térmica")


@app.command("test")
def test() -> None:
    """Ejecuta una impresión de prueba."""
    run_print_test()
    typer.echo("Impresión de prueba enviada.")
