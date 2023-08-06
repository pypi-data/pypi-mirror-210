import datetime

from gdshoplib.services.vk.vk import VK


class VKStats:
    def __init__(self, manager=None):
        self.manager = manager or VK()

    def members(self):
        # Возвращает список участников сообщества.
        result = self.manager.request(
            "groups.getMembers",
            params={
                "group_id": self.manager.settings.VK_GROUP_ID,
                "fields": [
                    "bdate",
                    "can_post",
                    "can_see_all_posts",
                    "can_see_audio",
                    "can_write_private_message",
                    "city",
                    "common_count",
                    "connections",
                    "contacts",
                    "country",
                    "domain",
                    "education",
                    "has_mobile",
                    "last_seen",
                    "lists",
                    "online",
                    "online_mobile",
                    "photo_100",
                    "photo_200",
                    "photo_200_orig",
                    "photo_400_orig",
                    "photo_50",
                    "photo_max",
                    "photo_max_orig",
                    "relation",
                    "relatives",
                    "schools",
                    "sex",
                    "site",
                    "status",
                    "universities",
                ],
            },
        )
        return result

    def products(self):
        # Возвращает информацию о товаре
        result = self.manager.request(
            "market.get",
            params={"owner_id": f"-{self.manager.settings.VK_GROUP_ID}", "extended": 1},
        )
        return result

    def community(
        self,
        timestamp_from: datetime.datetime = None,
        timestamp_to: datetime.datetime = None,
    ):
        # Возвращает статистику сообщества или приложения.
        result = self.manager.request(
            "stats.get",
            params={
                "group_id": self.manager.settings.VK_GROUP_ID,
                "timestamp_from": (
                    timestamp_from
                    or datetime.datetime.now() - datetime.timedelta(days=1)
                ).timestamp(),
                "timestamp_to": (timestamp_to or datetime.datetime.now()).timestamp(),
                "interval": "day",
                "extended": 1,
            },
        )
        return result
