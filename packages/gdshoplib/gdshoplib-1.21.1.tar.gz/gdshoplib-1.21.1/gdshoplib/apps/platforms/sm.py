import datetime

from lxml import etree, objectify

from gdshoplib.apps.platforms.yam import YandexMarketManager
from gdshoplib.packages.feed import Feed


class SberMarketManager(YandexMarketManager, Feed):
    KEY = "SM"

    def get_root(self):
        root = etree.Element("yml_catalog")
        objectify.deannotate(root, cleanup_namespaces=True, xsi_nil=True)
        root.attrib["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return root
