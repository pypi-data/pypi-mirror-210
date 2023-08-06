import time
from multiprocessing import Pool
from typing import Optional

import typer

from gdshoplib.apps.products.product import Product
from gdshoplib.packages.s3 import S3, SimpleS3Data
from gdshoplib.services.notion.database import Database

app = typer.Typer()


@app.command()
def warm(
    single: bool = typer.Option(False),
    with_badges: bool = typer.Option(False),
    loop_iteration: Optional[int] = typer.Option(None),
    sku: Optional[str] = typer.Option(None),
):
    while True:
        if sku:
            warm_product_media(Product.get(sku).id, with_badges)
            return
        if single:
            for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
                warm_product_media(product["id"], with_badges)
        else:
            with Pool(7) as p:
                for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
                    p.apply_async(warm_product_media, (product["id"], with_badges))
                p.close()
                p.join()

        if loop_iteration:
            time.sleep(loop_iteration)
        else:
            break


@app.command()
def clean():
    s3 = S3(SimpleS3Data(None, file_key=None))
    s3.clean(pattern="Contents[? !contains(Key, `feed.`)][]")


@app.command()
def search(file_key=None):
    s3 = S3(SimpleS3Data(None, file_key=None))
    for object in s3.search(pattern=file_key):
        print(object)


@app.command()
def count():
    count = 0
    for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
        count += len(Product(product["id"]).media)

    print(count)


@app.command()
def check(single: bool = typer.Option(False)):
    if single:
        for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
            media_check_action(product["id"])
    else:
        with Pool(3) as p:
            for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
                p.apply_async(media_check_action, (product["id"],))
            p.close()
            p.join()


###


def media_check_action(id):
    accepted_formats = (
        "png",
        "jpg",
        "jpeg",
    )
    product = Product(id)
    for media in Product(product.id).media:
        accepted = media.format in accepted_formats
        print(
            f"{media.file_key}: {media.exists()} {'ACCEPTED' if accepted else 'REJECTED'}"
        )


def warm_product_media(id, with_badges):
    for media in Product(id).media:
        media.fetch()
        print(f"{media.s3}: {media.exists()}")
        if with_badges and media.badges:
            render = media.apply_badges()
            badged = S3(
                SimpleS3Data(
                    render.content,
                    None,
                    render.info["mime"],
                    file_info={
                        "id": media.id,
                        "format": render.info["format"],
                        "prefix": "BADGED",
                    },
                    parent=media.parent,
                )
            )
            badged.put()
            print(f"{badged} {badged.exists()}")
