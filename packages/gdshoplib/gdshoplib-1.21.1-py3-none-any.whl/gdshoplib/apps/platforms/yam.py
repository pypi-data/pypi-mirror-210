import re

from lxml import etree, objectify

from gdshoplib.apps.platforms.base import Platform
from gdshoplib.core.settings import ProductSettings
from gdshoplib.packages.feed import Feed
from gdshoplib.services.notion.database import Database


class YandexMarketManager(Platform, Feed):
    KEY = "YAM"

    def get_categories(self):
        categories = Database(ProductSettings().CATEGORY_DB).pages()
        return [(self.fetch_id(i.id), i.title) for i in categories]

    @staticmethod
    def fetch_id(id):
        return str(sum([int(i) for i in re.sub(r"\D*", "", id)]))

    @property
    def product_filter(self):
        return dict(status_description="Готово", status_publication="Публикация")

    def get_shop(self):
        shop = objectify.Element("shop")

        shop.name = self.feed_settings.SHOP_NAME
        shop.company = self.feed_settings.COMPANY_NAME
        shop.url = self.feed_settings.SHOP_URL

        currencies = objectify.Element("currencies")
        currency = etree.Element("currency")
        currency.attrib["id"] = "RUB"
        currency.attrib["rate"] = "1"
        objectify.deannotate(currency, cleanup_namespaces=True, xsi_nil=True)
        objectify.deannotate(currencies, cleanup_namespaces=True, xsi_nil=True)
        currencies.append(currency)
        shop.currencies = currencies

        categories = objectify.Element("categories")
        for ind, k in enumerate(
            ["Все товары", "Спорт и отдых", "Конный спорт"], start=1
        ):
            category = etree.Element("category")
            category.attrib["id"] = str(ind)
            if ind - 1 != 0:
                category.attrib["parentId"] = str(ind - 1)
            category.text = k
            categories.append(category)

        for _id, name in self.get_categories():
            category = etree.Element("category")
            category.attrib["id"] = _id
            category.attrib["parentId"] = "3"
            category.text = name
            objectify.deannotate(category, cleanup_namespaces=True, xsi_nil=True)
            categories.append(category)

        shop.categories = categories
        objectify.deannotate(shop, cleanup_namespaces=True, xsi_nil=True)

        return shop

    def get_offer(self, product):
        appt = objectify.Element("offer")
        appt.attrib["id"] = product.sku
        appt.count = product.quantity
        if product.quantity == 0:
            appt.attrib["type"] = "on.demand"

        appt.currencyId = "RUB"
        appt.price = product.price.now
        if self.get_old_price(product):
            appt.oldprice = self.get_old_price(product)

        for image in product.images:
            appt.addattr("picture", self.get_media_url(image))

        appt.name = product.name
        appt.description = product.description.generate(self)
        appt.vendor = product.brand.title
        appt.categoryId = self.fetch_id(product.categories[0].id)
        appt.barcode = product.barcode.code if product.barcode else 0
        appt.dimensions = (
            product.dimensions if product.dimensions else "0/0/0"
        )  # Длина, ширина, высота в упаковке.
        appt.weight = product.weight if product.weight else 0

        objectify.deannotate(appt, cleanup_namespaces=True, xsi_nil=True)
        return appt
