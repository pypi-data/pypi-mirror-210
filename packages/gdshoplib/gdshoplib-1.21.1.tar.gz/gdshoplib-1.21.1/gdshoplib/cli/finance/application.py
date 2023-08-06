import typer

from gdshoplib.cli.finance.store import app as store

app = typer.Typer()

app.add_typer(store, name="store")

if __name__ == "__main__":
    app()
