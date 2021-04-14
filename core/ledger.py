from core.order import Order
from core.cash_table import CashTable
from core.order_table import OrderTable
from core.position_table import PositionTable


class Ledger:
    """
    Ledger는 원장이라는 뜻이며, 프로그램 상에서 발생하는 모든 액션을 기록하는 목적을 가지고 있다.

    실제 주문 발생과 같은 역할은 모두 외부에서 발생시키며, 원장은 철저히 데이터 관리에만 집중한다.
    """

    def __init__(self):
        self.cash_table = CashTable()
        self.order_table = OrderTable()
        self.position_table = PositionTable()

    def order_hash(self, symbol, price, quantity, side, order_type, meta):
        return Order.make_order_hash(symbol=symbol,
                                     price=price,
                                     quantity=quantity,
                                     side=side,
                                     order_type=order_type,
                                     meta=meta)

    def get_cash(self, strategy_name, meta=None):
        return self.cash_table.get_cash(strategy_name=strategy_name, meta=meta)

    def update_cash(self, strategy_name, amount, meta=None):
        self.cash_table.update_cash(strategy_name=strategy_name, amount=amount, meta=meta)

    def get_orders(self, strategy_name):
        return self.order_table.get_orders(strategy_name=strategy_name)

    def get_order(self, strategy_name, order_number):
        return self.order_table.get_order(strategy_name=strategy_name, order_number=order_number).__dict__

    def get_positions(self, strategy_name):
        return self.position_table.get_positions(strategy_name=strategy_name)

    def get_position(self, strategy_name, symbol):
        return self.position_table.get_position(strategy_name=strategy_name, symbol=symbol).__dict__

    def init_order(self, strategy_name, symbol, price, quantity, side, order_type, meta=None):
        order = Order(strategy_name=strategy_name,
                      symbol=symbol,
                      price=price,
                      quantity=quantity,
                      side=side,
                      order_type=order_type,
                      meta=meta)
        self.order_table.add_order(order)
        return order.hash

    def register_order(self, order_number, order_hash):
        return self.order_table.make_open_order(order_hash=order_hash, order_number=order_number)

    def cancel_order(self, strategy_name, order_number):
        pass

    def fill_order(self, strategy_name, order_number, price, quantity, position_amount=None):
        order = self.order_table.fill_order(strategy_name=strategy_name,
                                            order_number=order_number,
                                            quantity=quantity,
                                            return_order=True)
        order_base_info = order.order_base_info
        self.position_table.update_position(strategy_name=strategy_name,
                                            symbol=order_base_info['symbol'],
                                            side=order_base_info['side'],
                                            price=price,
                                            quantity=quantity,
                                            position_amount=position_amount)


if __name__ == '__main__':
    strategy_name = 'strategy_1'

    ledger = Ledger()

    ledger.update_holding(strategy_name, 'cash', 1000)

    order_params = {
        'strategy_name': strategy_name,
        'symbol': '005930',
        'quantity': 2,
        'price': 100,
        'side': 'BUY',
        'order_type': 'LIMIT',
        'meta': '신한'
    }

    # client(strategy) sends order
    order_hash = ledger.init_order(**order_params)

    order_number = 'ordernumber123'
    # client's order is registered from real exchange (has order number)
    st = ledger.register_order(order_number, order_hash)

    ledger.fill_order(st, order_number, 100, 1)
    # ledger.fill_order(strategy_name, order_number, 100, 1)

    print(ledger.order_table.order_table)