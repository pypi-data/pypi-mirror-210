from gdshoplib.services.vk.vk import VK


class VKPage:
    def __init__(self, manager=None):
        self.manager = manager or VK()

    def set_enable(self):
        response = self.manager.request(
            "groups.enableOnline",
            params={"group_id": self.manager.settings.VK_GROUP_ID},
        )
        return bool(
            response.get("response") or response.get("error", {}).get("error_code") == 8
        )

    def set_disable(self):
        response = self.manager.request(
            "groups.disableOnline",
            params={"group_id": self.manager.settings.VK_GROUP_ID},
        )
        return bool(
            response.get("response") or response.get("error", {}).get("error_code") == 8
        )

    def get_online_status(self):
        status = self.manager.request(
            "groups.getOnlineStatus",
            params={"group_id": self.manager.settings.VK_GROUP_ID},
        )["response"].get("status")
        return status == "online"
