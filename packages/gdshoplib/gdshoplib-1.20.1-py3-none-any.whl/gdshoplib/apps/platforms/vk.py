from pydantic import BaseModel

from gdshoplib.apps.platforms.base import Platform
from gdshoplib.packages.feed import Feed


class VKProductModel(BaseModel):
    ...


class VKManager(Platform, Feed):
    DESCRIPTION_TEMPLATE = "vk.txt"
    KEY = "VK"

    @property
    def product_filter(self):
        return dict(status_description="Готово")

    # def get_products(self) -> List[VKProductModel]:
    #     ...

    # def push_feed(self):
    #     # Обновить товары в VK
    #     ...
