import json
import time
from multiprocessing import Pool
from typing import List, Optional

import typer
import ujson
from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger
from pydantic import BaseModel

from gdshoplib.apps.products.product import Product
from gdshoplib.core.settings import NotionSettings
from gdshoplib.packages.cache import KeyDBCache
from gdshoplib.services.notion.database import Database
from gdshoplib.services.notion.notion import Notion

app = typer.Typer()


@app.command()
def clean(id: Optional[str] = typer.Option(None)):
    # TODO: сделать удаление по ID
    KeyDBCache().clean(r"[blocks|pages|databases]*")


@app.command()
def listen(topic: List[str]):
    for message in KeyDBCache().subscribe(topic):
        print(message)


@app.command()
def upload(
    sku: Optional[str] = typer.Option(None),
    platform: Optional[str] = typer.Option(None),
):
    producer = KafkaProducer(
        bootstrap_servers=NotionSettings().KAFKA_BROKER,
        value_serializer=lambda m: ujson.dumps(m).encode("utf8"),
        request_timeout_ms=1000,
    )

    class Message(BaseModel):
        id: str
        data: str
        version_md5: Optional[str]
        timestamp: str
        data_md5: Optional[str]
        parrent_id: str

        def send(self):
            # - Отправить в kafka
            future = producer.send(NotionSettings().KAFKA_TOPIC, self.dict())
            try:
                future.get(timeout=10)
            except KafkaError:
                # Decide what to do if produce request failed...
                logger.exception()
            else:
                print(f"DONE: {self.id}")

    # Загрузить в базу объекты
    notion = Notion()
    # - Проитерироваться по списку страниц
    for page in notion.search():
        Message(
            id=page["id"],
            data=json.dumps(page),
            parrent_id=page["parent"][page["parent"]["type"]],
            timestamp=str(time.time()),
        ).send()


@app.command()
def warm(
    only_exists: bool = typer.Option(False),
    single: bool = typer.Option(False),
    only_edited: bool = typer.Option(True),
    sku: Optional[str] = typer.Option(None),
    loop_iteration: Optional[int] = typer.Option(None),
):
    while True:
        if sku:
            cache_warm_func(Product.get(sku).id)
            return

        if single:
            with Database(
                Product.SETTINGS.PRODUCT_DB, notion=Notion(caching=True)
            ) as database:
                params = {}
                if only_edited and database.get_update_time():
                    print(f"Фильтрация от даты: {database.get_update_time()}")
                    params = database.edited_filter()

                for product in database.pages(params=params):
                    skipped = False
                    if only_exists:
                        if KeyDBCache().exists(product["id"]):
                            print(f"{product['id']}: SKIPPED")
                            skipped = True

                    if not skipped:
                        cache_warm_func(product["id"])
        else:
            with Pool(3) as p:
                with Database(
                    Product.SETTINGS.PRODUCT_DB, notion=Notion(caching=True)
                ) as database:
                    params = {}
                    if only_edited and database.get_update_time():
                        print(f"Фильтрация от даты: {database.get_update_time()}")
                        params = database.edited_filter()

                    for product in database.pages(params=params):
                        skipped = False
                        if only_exists:
                            if KeyDBCache().exists(product["id"]):
                                print(f"{product['id']}: SKIPPED")
                                skipped = True

                        if not skipped:
                            p.apply_async(cache_warm_func, (product["id"],))
                p.close()
                p.join()

        if loop_iteration:
            print("-" * 20)
            time.sleep(loop_iteration)
        else:
            break


@app.command()
def count():
    print(KeyDBCache().count())


@app.command()
def check(single: bool = typer.Option(False)):
    if single:
        for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
            cache_check_action(product["id"])
    else:
        with Pool(3) as p:
            for product in Database(Product.SETTINGS.PRODUCT_DB).pages():
                p.apply_async(cache_check_action, (product["id"],))
            p.close()
            p.join()


#####


def cache_check_action(id):
    for block in Notion().get_blocks(id):
        exists = KeyDBCache().exists(block["id"])
        print(f"{block['id']}: {exists}")


def cache_warm_func(id):
    product = Product(id)
    try:
        product.warm()
    except AttributeError:
        print(f"!= Пропущено {product.sku}: {product.last_edited_time}")
    else:
        print(f"{product.sku}: {product.last_edited_time}")
