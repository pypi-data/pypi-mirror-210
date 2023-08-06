from multiprocessing import Pool
from typing import Optional

import typer

from gdshoplib.apps.products.product import Product
from gdshoplib.services.notion.notion import Notion

app = typer.Typer()


@app.command()
def scan(
    single: bool = typer.Option(False),
    sku: Optional[str] = typer.Option(None),
):
    """Отсканировать и проставить коды"""
    if sku:
        warm_func(Product.get(sku).id)
        return

    if single:
        for page in Product.query(
            notion=Notion(caching=True),
            params={
                "filter": {
                    "and": [
                        {"property": "Штрихкод", "files": {"is_not_empty": True}},
                        {"property": "Код штрихкода", "number": {"is_empty": True}},
                    ]
                }
            },
        ):
            warm_func(page["id"])
    else:
        with Pool(3) as p:
            for page in Product.query(
                notion=Notion(caching=True),
                params={
                    "filter": {
                        "and": [
                            {
                                {
                                    "property": "Штрихкод",
                                    "files": {"is_not_empty": True},
                                },
                                {
                                    "property": "Код штрихкода",
                                    "number": {"is_empty": True},
                                },
                            },
                        ]
                    }
                },
            ):
                p.apply_async(warm_func, (page["id"],))
            p.close()
            p.join()


def warm_func(id):
    product = Product(id)
    if not product.barcode_image_field:
        return
    if not product.barcode_code_field:
        if not product.barcode:
            print(f"Штрихкод не прочитан: {product}")
            return

        product.notion.update_prop(
            product.id,
            params={"properties": {"Код штрихкода": {"number": product.barcode.code}}},
        )
        print(product)
