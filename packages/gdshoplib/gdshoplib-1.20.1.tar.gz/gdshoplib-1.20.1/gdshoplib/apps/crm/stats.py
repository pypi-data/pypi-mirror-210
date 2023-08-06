import numpy

from gdshoplib.apps.crm.orders import Order
from gdshoplib.services.notion.notion import Notion


class Statistic:
    def avg_price(cls, filter_type="complited"):
        params = Order.list_filter(filter_type=filter_type)
        notion = Notion(caching=True)
        return numpy.average(
            [order.price for order in Order.query(notion=notion, params=params)]
        )

    def percentile(self, filter_type="complited"):
        params = Order.list_filter(filter_type=filter_type)
        notion = Notion(caching=True)
        return numpy.percentile(
            [order.price for order in Order.query(notion=notion, params=params)], 5
        )
