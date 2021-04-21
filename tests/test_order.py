from unittest import TestCase

from core.order import Order, OrderState


class OrderTest(TestCase):

    def test_can_init_order(self):
        strategy_name = 'strategy_1'
        symbol = '005930'
        price = 50000
        quantity = 2
        side = 'BUY'
        order_type = 'LIMIT'
        meta = 'shinhan.stock'

        order = Order(strategy_name=strategy_name,
                      symbol=symbol,
                      price=price,
                      quantity=quantity,
                      side=side,
                      order_type=order_type,
                      meta=meta)

        self.assertTrue(order.ORDER_STATE == OrderState.INIT)