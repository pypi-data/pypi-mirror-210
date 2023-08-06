from multiprocessing import Pool

import typer

from gdshoplib.apps.platforms import Platform, search_platform
from gdshoplib.apps.products.product import Product
from gdshoplib.services.notion.database import Database
from gdshoplib.services.notion.notion import Notion

app = typer.Typer()


@app.command()
def regenerate(single: bool = typer.Option(False)):
    if single:
        for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
            generate_description(product["id"])
    else:
        with Pool(3) as p:
            for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
                p.apply_async(generate_description, (product["id"],))
            p.close()
            p.join()


@app.command()
def check(single: bool = typer.Option(False)):
    with Pool(3) as p:
        for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
            p.apply_async(description_check_action, (product["id"],))
        p.close()
        p.join()


###


def generate_description(id):
    product = Product(id)
    product.description.warm_description_blocks()
    for platform, block in product.description.description_blocks.items():
        key = platform.split(":")[-1]

        new_description = product.description.generate(search_platform(key))
        Notion().update_block(
            block.id,
            params={"code": {"rich_text": [{"text": {"content": new_description}}]}},
        )
        print(f"{product.sku}: {platform}")


def description_check_action(id):
    product = Product(id)
    for platform_manager in Platform.__subclasses__():
        block = product.description.get_description_block(
            platform_key=platform_manager.KEY
        )
        print(f'{product.sku} {platform_manager}: {block.check if block else "None"}')
