import time
from multiprocessing import Pool
from typing import Optional

import typer

from gdshoplib.apps.products.product import Product
from gdshoplib.services.notion.database import Database

app = typer.Typer()


@app.command()
def update(
    sku: Optional[str] = typer.Option(None),
    single: bool = typer.Option(False),
    loop_iteration: Optional[int] = typer.Option(None),
):
    while True:
        if sku:
            price_update_action(Product.get(sku).id)
            return

        if single:
            for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
                price_update_action(product["id"])
        else:
            with Pool(3) as p:
                for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
                    p.apply_async(price_update_action, (product["id"],))
                p.close()
                p.join()

        if loop_iteration:
            time.sleep(loop_iteration)
        else:
            break


###


def price_update_action(id):
    product = Product(id)
    props_map = {
        "price_now": dict(name="Текущая Цена", value=product.price.now),
        "price_kit": dict(name="Цена комплекта", value=product.price.get_kit_price()),
        "price_neitral": dict(name="Безубыточность", value=product.price.neitral),
        "price_current_discount": dict(
            name="Текущая Скидка", value=product.price.current_discount
        ),
        "price_agent": dict(name="Агентская Цена", value=product.price.neitral),
        "price_agent_kit": dict(
            name="Агентский комплект",
            value=product.price.get_kit_price(base_price="neitral"),
        ),
        "price_gross": dict(name="Себестоимость", value=product.price.gross),
    }

    for k, v in props_map.items():
        if not product[k] and not v["value"] or product[k] == v["value"]:
            continue

        product.notion.update_prop(
            product.id, params={"properties": {v["name"]: {"number": v["value"]}}}
        )
        print(f'{product.sku}: {v["name"]} ({v["value"]})')
