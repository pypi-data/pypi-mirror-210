import typer

from gdshoplib.cli.product.barcode import app as barcode
from gdshoplib.cli.product.cache import app as cache
from gdshoplib.cli.product.controle import app as controle
from gdshoplib.cli.product.description import app as description
from gdshoplib.cli.product.feed import app as feed
from gdshoplib.cli.product.media import app as media
from gdshoplib.cli.product.price import app as price

app = typer.Typer()

app.add_typer(cache, name="cache")
app.add_typer(barcode, name="barcode")
app.add_typer(controle, name="controle")
app.add_typer(description, name="description")
app.add_typer(feed, name="feed")
app.add_typer(media, name="media")
app.add_typer(price, name="price")

if __name__ == "__main__":
    app()
