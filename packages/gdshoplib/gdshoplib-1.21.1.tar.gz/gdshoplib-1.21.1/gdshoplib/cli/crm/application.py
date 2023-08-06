import typer

from gdshoplib.cli.crm.order import app as order
from gdshoplib.cli.crm.stats import app as stats

app = typer.Typer()

app.add_typer(order, name="order")
app.add_typer(stats, name="stats")


if __name__ == "__main__":
    app()
