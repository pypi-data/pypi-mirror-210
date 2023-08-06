from typing import List, Optional

from pydantic import BaseModel

from gdshoplib.services.vk.vk import VK


class VKProduct(BaseModel):
    category: dict
    id: int
    description: Optional[str]
    price: dict
    title: str
    photos: List[dict]
    likes: dict
    reposts: dict
    views_count: int
    date: int
    sku: str
    raw: Optional[dict]

    @classmethod
    def parse_obj(cls, obj):
        result = super(VKProduct, cls).parse_obj(obj)
        result.raw = obj
        return result


class VKNewProduct(BaseModel):
    name: str
    description: str
    price: int
    old_price: Optional[int]
    main_photo_id: int
    photo_ids: Optional[List[Optional[int]]]
    sku: str


class VKEditProduct(BaseModel):
    name: str


class VKMarket:
    def __init__(self, manager=None):
        self.manager = manager or VK()

    def list(self):
        result = self.manager.request(
            "market.get",
            params={
                "owner_id": f"-{self.manager.settings.VK_GROUP_ID}",
                "extended": 1,
                "with_disabled": 1,
                "need_variants": 1,
            },
        )["response"]
        if result:
            return [VKProduct.parse_obj(item) for item in result["items"]]

    def get(self, sku):
        result = list(filter(lambda d: d.sku == sku, self.list()))
        if not result:
            return
        return result[0]

    def add(self, product: VKNewProduct):
        assert isinstance(
            product, VKNewProduct
        ), f"Продукт передан не того типа: {product.__class__} != VKNewProduct"

        return self.manager.request(
            "market.add",
            params={
                "owner_id": f"-{self.manager.settings.VK_GROUP_ID}",
                "category_id": self.manager.settings.VK_CATEGORY_ID,
                **product.dict(),
            },
        )

    def edit(self, sku, product: VKEditProduct):
        assert isinstance(
            product, VKEditProduct
        ), f"Продукт передан не того типа: {product.__class__} != VKNewProduct"

        item = self.get(sku)
        return self.manager.request(
            "market.edit",
            params={
                "owner_id": f"-{self.manager.settings.VK_GROUP_ID}",
                "item_id": item.id,
                **product.dict(),
            },
        )

    def delete(self, sku):
        item = self.get(sku)
        return self.manager.request(
            "market.delete",
            params={
                "owner_id": f"-{self.manager.settings.VK_GROUP_ID}",
                "item_id": item.id,
            },
        )

    def album_get(self, sku):
        ...

    def album_create(self, sku):
        ...

    def album_edit(self, sku):
        ...

    def album_delete(self, sku):
        ...

    def album_add(self, sku):
        ...
