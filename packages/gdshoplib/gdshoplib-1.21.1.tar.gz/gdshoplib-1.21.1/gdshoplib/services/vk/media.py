import logging

from gdshoplib.services.vk.vk import VK

logger = logging.getLogger(__name__)


class VKMedia:
    def __init__(self, manager=None):
        self.manager = manager or VK()

    def get_upload_url(self):
        result = self.manager.request(
            "photos.getMarketUploadServer",
            params={"group_id": self.manager.settings.VK_GROUP_ID},
        )
        if result:
            return result["response"]["upload_url"]

    def _upload_photo(self, photo):
        return self.manager.request(
            None,
            params={},
            url=self.get_upload_url(),
            http_method="post",
            files={"file": (photo.name.split("/")[-1], photo)},
        )

    def upload(self, photo):
        upload_result = self._upload_photo(photo)
        result = self.manager.request(
            "photos.saveMarketPhoto",
            params={"group_id": self.manager.settings.VK_GROUP_ID, **upload_result},
        )
        if result:
            return result["response"][0]

    def delete(self, id):
        result = self.manager.request(
            "photos.delete",
            params={
                "owner_id": f"-{self.manager.settings.VK_GROUP_ID}",
                "photo_id": id,
            },
        )
        if result:
            return bool(result["response"] == 1)

    def get(self, id):
        # TODO: сделать работу с объектом
        result = self.manager.request(
            "photos.getById",
            params={
                "photos": f"-{self.manager.settings.VK_GROUP_ID}_{id}",
            },
        )
        if result.get("error"):
            if result["error"]["error_code"] == 200:
                return
            logger.warning(result)
            return
        else:
            return result["response"][0]
