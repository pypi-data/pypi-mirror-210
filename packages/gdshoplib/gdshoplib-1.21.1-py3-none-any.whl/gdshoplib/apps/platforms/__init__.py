from .avito import AvitoManager
from .base import Platform
from .instagram import InstagramManager
from .ok import OkManager
from .sm import SberMarketManager
from .tg import TgManager
from .ula import UlaManager
from .vk import VKManager
from .yam import YandexMarketManager


def search_platform(key):
    for platform_class in Platform.__subclasses__():
        if platform_class.KEY.lower() == key.lower():
            return platform_class


__all__ = (
    "AvitoManager",
    "InstagramManager",
    "OkManager",
    "TgManager",
    "UlaManager",
    "VKManager",
    "YandexMarketManager",
    "SberMarketManager",
    "Platform",
    "search_platform",
)
