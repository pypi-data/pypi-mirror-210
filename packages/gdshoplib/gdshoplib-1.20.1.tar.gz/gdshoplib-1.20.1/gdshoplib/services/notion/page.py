import requests
from dateutil.parser import parse

from gdshoplib.packages.renderer import ImageRenderer
from gdshoplib.services.notion.base import BasePage
from gdshoplib.services.notion.block import Block
from gdshoplib.services.notion.models.props import PropModel
from gdshoplib.services.notion.notion import Notion


class Page(BasePage):
    def refresh(self):
        Notion(caching=True).get_page(self.id)
        self.initialize()

    def initialize(self):
        super(Page, self).initialize()
        self.properties = PageProperty(self.page)

    def blocks(self, filter=None):
        if not filter:
            for block in self.notion.get_blocks(self.id):
                yield Block(block["id"], notion=self.notion, parent=self)
            return

        for block in self.notion.get_blocks(self.id):
            for k, v in filter.items():
                block = Block(block["id"], notion=self.notion, parent=self)
                if str(block.__getattr__(k)).lower() == str(v).lower():
                    yield block

    def __getattr__(self, attr):
        try:
            return super(Page, self).__getattr__(attr)
        except PropGetexception:
            self.refresh()
            return super(Page, self).__getattr__(attr)

    def warm(self):
        self.refresh()
        for block in self.notion.get_blocks(self.id):
            Block(block["id"], parent=self).refresh()

    def commit(self):
        # Проитерироваться по изменениям и выполнить в Notion
        ...

    def to_json(self):
        # Вернуть товар в json
        ...


class PageProperty:
    def __init__(self, page):
        self.page = page

    def __getitem__(self, key):
        return self.__dict__.get(key) or self.__search_content(key)

    def __getattr__(self, key):
        return self[key]

    def __search_content(self, key):
        prop = self.get_model_by_key(key)
        return prop.get_data()

    def get_model_by_name(self, name):
        model = PropModel(name=name, page=self.page)
        fields = []
        for key, field_list in self.properties_keys_map.items():
            for field in field_list:
                if field["name"] == name:
                    fields.append(field)
        model.fields = fields
        return model

    def get_model_by_key(self, key):
        model = PropModel(key=key, page=self.page)
        model.fields = self.properties_keys_map.get(key)
        return model

    def get_model_by_id(self, id):
        model = PropModel(id=id, page=self.page)
        for key, field_list in self.properties_keys_map.items():
            for field in field_list:
                if field["id"] == id:
                    model.fields = [field]
        return model

    def __str__(self) -> str:
        return f"{self.__class__}"

    def __repr__(self) -> str:
        return f"{self.__class__}"

    def relation_handler(self, page_id_in_list):
        _id = page_id_in_list[0]["id"]
        return Page(_id)

    def relation_list_handler(self, page_ids):
        result = []
        for _id in page_ids:
            result.append(Page(_id["id"]))
        return result

    def date_handler(self, date):
        if not date:
            return
        elif "start" in date:
            return parse(date["start"]).date()

        return parse(date).date()

    def image_handler(self, image):
        if not image:
            return

        response = requests.get(image[0]["file"]["url"])
        if not response.ok:
            raise PropGetexception

        return ImageRenderer(response.content)

    def files_field_handler(self, files):
        if not files:
            return None
        if len(files) == 1:
            return files[0]["file"]["url"]
        return [file["file"]["url"] for file in files]

    @property
    def properties_keys_map(self):
        return {
            "title": (
                dict(name="Name", id="title"),
                dict(name="Код", id="title"),
            ),
            "error": (dict(name="Ошибка", id="OD%60%7C"),),
            "edited_by": (dict(name="Last edited by", id="~%7BrF"),),
            "work": (dict(name="Использовать", id="bAcI"),),
            "created_time": (
                dict(name="Created time", id="v%5Dsj", handler=self.date_handler),
            ),
            "short_description": (dict(name="Короткое описание", id="u_tU"),),
            "size": (
                dict(name="Размер", id="taW%3B"),
                dict(name="Размер", id="NUuD"),
            ),
            "notes_field": (dict(name="Примечания", id="sXND"),),
            "quantity": (dict(name="Кол-во", id="pXTy"),),
            "edited_time": (
                dict(name="Last edited time", id="mVEw", handler=self.date_handler),
            ),
            "collection": (dict(name="Коллекция", id="W%5BhI"),),
            "name": (dict(name="Название на русском", id="Tss%5D"),),
            "created_by": (dict(name="Created by", id="TbyK"),),
            "kit_field": (
                dict(
                    name="Комплект", id="QV%5D%5D", handler=self.relation_list_handler
                ),
            ),
            "tags_field": (dict(name="Теги", id="MqdC"),),
            "status_description": (dict(name="Описание", id="MUl%7C"),),
            "status_publication": (dict(name="Публикация", id="BeEA"),),
            "color": (dict(name="Цвет", id="Jvku"),),
            "weight": (dict(name="Вес", id="Q%3FVy"),),
            "dimensions": (dict(name="Габариты", id="Q~eD"),),
            "specifications_field": (
                dict(name="Материалы / Характеристики", id="COmf"),
            ),
            "barcode_image_field": (
                dict(name="Штрихкод", id="Yiu%7D", handler=self.image_handler),
            ),
            "barcode_code_field": (dict(name="Код штрихкода", id="Uzsu"),),
            "original_name": (dict(name="Оригинальное название", id="%5CiXC"),),
            "price_neitral": (dict(name="Безубыточность", id="VmWm"),),
            "price_now": (dict(name="Текущая Цена", id="Ddaz"),),
            "price_kit": (dict(name="Цена комплекта", id="Dwfs"),),
            "price_current_discount": (dict(name="Текущая Скидка", id="syrp"),),
            "price_agent": (dict(name="Агентская Цена", id="vC%5E%3D"),),
            "price_agent_kit": (dict(name="Агентский комплект", id="M%60HY"),),
            "price_gross": (dict(name="Себестоимость", id="d%3DhO"),),
            "avito_id": (dict(name="avito_id", id="voQ%3E"),),
            "vk_id": (dict(name="vk_id", id="Ve%7Ca"),),
            "discount_from_date": (
                dict(name="Дата поставки", id="%60_a%3D", handler=self.date_handler),
            ),
            "badge_field": (
                dict(name="🎖️ Бейджи", id="%3CU_H", handler=self.relation_list_handler),
            ),
            "file": (dict(name="Файл", id="uK%3CN", handler=self.files_field_handler),),
            "coordinates": (dict(name="Координаты", id="XU%7C%3F"),),
            "transparency": (dict(name="Прозрачность", id="RHj%5B"),),
            "sku": (dict(name="Наш SKU", id="BKOs"),),
            "sku_s": (dict(name="SKU поставщика", id="BHve"),),
            "price_eur": (dict(name="Цена (eur)", id="AyqD"),),
            "brand": (
                dict(name="Бренд", id="gk%40%3B", handler=self.relation_handler),
            ),
            "categories": (
                dict(name="Категории", id="%7CFzB", handler=self.relation_list_handler),
            ),
            "price_coefficient": (
                dict(name="Наценка", id="HjFs"),
                dict(name="Наценка", id="YsUp"),
                dict(name="Наценка", id="lNgd"),
            ),
            "order_type": (dict(name="Тип заказа", id="%40%5Eql"),),
            "status": (dict(name="Status", id="EGwa"),),
            "promocodes": (
                dict(
                    name="🎫 Промокоды",
                    id="L%5CU%60",
                    handler=self.relation_list_handler,
                ),
            ),
            "pay_url": (dict(name="Оплата", id="%5D%7BRo"),),
            "price_result": (dict(name="Итого", id="bAsK"),),
            "products_field": (
                dict(name="🥇 Товары", id="e%3BIp", handler=self.relation_list_handler),
            ),
            "customer": (
                dict(name="Клиент", id="hGXc", handler=self.relation_handler),
            ),
            "discount": (
                dict(name="Скидка", id="k%5EOl"),
                dict(name="Скидка", id="vI~q"),
                dict(name="Персональная скидка", id="iXkC"),
            ),
            "platform": (
                dict(name="Откуда", id="n_pE", handler=self.relation_handler),
            ),
            "nps": (dict(name="NPS", id="%7Biv%7B", handler=self.relation_handler),),
            "pk": (dict(name="ID заказа", id="%7CQ%5Dy"),),
            "transcription": (dict(name="Расчеты", id="~g~T"),),
            "profit_field": (dict(name="Прибыль", id="MaSy"),),
            "max_discount_field": (dict(name="max Скидка", id="%7DsC%3B"),),
            "key": (
                dict(
                    name="Ключ",
                    id="P%7CTt",
                ),
            ),
            "rejection_reason": (
                dict(
                    name="Причина отказа",
                    id="P%7CTt",
                ),
            ),
        }


class PropGetexception(Exception):
    ...
