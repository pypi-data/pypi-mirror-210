import typer

from gdshoplib.cli.service.avito import app as avito
from gdshoplib.cli.service.vk import app as vk

app = typer.Typer()

app.add_typer(vk, name="vk")
app.add_typer(avito, name="avito")

if __name__ == "__main__":
    app()
