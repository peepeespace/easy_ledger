from order import Order, OrderQueue, OrderTable


class Ledger:
    """
    Ledger는 원장이라는 뜻이며, 프로그램 상에서 발생하는 모든 액션을 기록하는 목적을 가지고 있다.

    실제 주문 발생과 같은 역할은 모두 외부에서 발생시키며, 원장은 철저히 데이터 관리에만 집중한다.
    """

    def __init__(self):
        self.order_queue = OrderQueue()
        self.order_table = OrderTable()

    def order_hash(self, symbol, quantity, price, side, order_type, meta):
        return Order.make_order_hash(symbol=symbol,
                                     quantity=quantity,
                                     price=price,
                                     side=side,
                                     order_type=order_type,
                                     meta=meta)

    def get_orders(self, strategy_name):
        return self.order_table.get_strategy_orders(strategy_name=strategy_name)

    def init_order(self, strategy_name, symbol, quantity, price, side, order_type, meta=None):
        order = Order(strategy_name=strategy_name,
                      symbol=symbol,
                      quantity=quantity,
                      price=price,
                      side=side,
                      order_type=order_type,
                      meta=meta)
        self.order_queue.add_order(order.hash)
        self.order_table.add_order(order)
        return order.hash

    def register_order(self, order_number, order_hash):
        return self.order_table.make_open_order(order_hash=order_hash, order_number=order_number)

    def fill_order(self, strategy_name, order_number, quantity):
        self.order_table.fill_order(strategy_name=strategy_name,
                                    order_number=order_number,
                                    quantity=quantity)


if __name__ == '__main__':
    ledger = Ledger()

    # order_params = {
    #     'strategy_name': 'strategy_1',
    #     'symbol': '005930',
    #     'quantity': 2,
    #     'price': 100,
    #     'side': 'LONG',
    #     'order_type': 'LIMIT',
    #     'meta': '신한'
    # }
    #
    # # client(strategy) sends order
    # order_hash = ledger.init_order(**order_params)
    #
    # order_number = 'ordernumber123'
    # # client's order is registered from real exchange (has order number)
    # strategy_name = ledger.register_order(order_number, order_hash)
    #
    # ledger.fill_order(strategy_name, order_number, 1)

    print(ledger.order_table.order_table)