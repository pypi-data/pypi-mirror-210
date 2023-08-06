from typing import Optional

import typer

from gdshoplib.apps.products.product import Product
from gdshoplib.services.notion.notion import Notion

app = typer.Typer()


@app.command()
def sku_set():
    for page in Product.query(
        notion=Notion(caching=True),
        params={
            "filter": {
                "and": [
                    {"property": "Наш SKU", "rich_text": {"is_empty": True}},
                    {"property": "Цена (eur)", "number": {"is_not_empty": True}},
                ]
            }
        },
    ):
        sku = page.generate_sku()
        while not Product.query(filter={"sku": sku}):
            sku = page.generate_sku()

        page.notion.update_prop(
            page.id, params={"properties": {"Наш SKU": [{"text": {"content": sku}}]}}
        )
        print(Product(page.id).sku)


@app.command()
def update_sku_naming(sku: Optional[str] = typer.Option(None)):
    sku_filter = {"equals": sku} if sku else {"is_not_empty": True}
    for page in Product.query(
        notion=Notion(caching=True),
        params={
            "filter": {
                "and": [
                    {"property": "Наш SKU", "rich_text": sku_filter},
                    {"property": "Описание", "status": {"equals": "Готово"}},
                ]
            }
        },
    ):
        title = f"{page.name.strip()}:{page.sku}"
        if page.title != title:
            if not page.original_name:
                page.notion.update_prop(
                    page.id,
                    params={
                        "properties": {
                            "Оригинальное название": [{"text": {"content": page.title}}]
                        }
                    },
                )
            page.notion.update_prop(
                page.id,
                params={"properties": {"title": [{"text": {"content": title}}]}},
            )
            print(title)
