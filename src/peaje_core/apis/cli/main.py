import typer

from peaje_core.apis.cli.printer import app as printer_app

app = typer.Typer(help="peaje-core: comandos de administración")
app.add_typer(printer_app, name="printer")

if __name__ == "__main__":
    app()
