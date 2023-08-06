class Storage:
    def amount(self, products, base_price="net"):
        result = 0
        for product in products:
            result += product.price[base_price] * product.quantity
        return result
