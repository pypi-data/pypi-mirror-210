import typer

from gdshoplib.apps.finance.storage import Storage
from gdshoplib.apps.products.product import Product

app = typer.Typer()


@app.command()
def amount(base_price="now"):
    params = {"filter": {"property": "Кол-во", "number": {"greater_than": 0}}}
    print(
        f"{base_price}: {Storage().amount(Product.query(params=params), base_price=base_price)}"
    )
