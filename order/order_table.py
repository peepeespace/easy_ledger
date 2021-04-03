import os
import pickle

from order.api import OrderState


class OrderTable:
    """
    Order 관련된 meta 데이터를 저장하기 위한 수단
    예를 들어서 동일한 종류의 주문을 어떤 전략들이 현재 넣은 상태인지 등

    hash값이 같은 경우도 발생할 수 있기 때문에 (다른 전략이 같은 종류의 주문을 연속해서 넣는 경우)
    strategies_with_current_order과 같은 meta 데이터로 이를 관리한다.
    """

    CACHE_NAME = 'OrderTable.pkl'

    def __init__(self):
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.CACHE_NAME):
            f = open(self.CACHE_NAME, 'rb')
            cached = pickle.load(f)
            self.order_table = cached.order_table
            self.order_meta = cached.order_meta
        else:
            self.order_table = {}
            self.order_meta = {}
            self._save_state()

    def _save_state(self):
        with open(self.CACHE_NAME, 'wb') as f:
            pickle.dump(self, f)

    def add_order(self, order):
        """
        equal_orders: 같은 내용의 주문을 여러개의 전략 혹은 하나의 전략에서 연속 발생할 수 있기 때문에 관리 필요
        """
        if order.init_id not in self.order_table:
            self.order_table[order.init_id] = order

        if order.hash not in self.order_meta:
            self.order_meta[order.hash] = {
                'equal_orders': [order]
            }
        else:
            self.order_meta[order.hash]['equal_orders'].insert(0, order)

        self._save_state()

    def register_order(self, order_hash):
        """
        add된 order를 실제 주문 거래소(소스)에서 접수가 완료된 것을 확인한 후 register된 order를 리턴하는 역할

        먼저 주문을 init한 전략의 주문이 먼저 체결된다는 가정하에 먼저 등록된 order를 pop하여 리턴한다.
        """
        try:
            order = self.order_meta[order_hash]['equal_orders'].pop()
            if not self.order_meta[order_hash]['equal_orders']:
                del self.order_meta[order_hash]
            self._save_state()
            return order
        except:
            return

    def make_open_order(self, order_hash, order_number):
        order = self.register_order(order_hash)
        if order is not None:
            order.make_open_order(order_number)
            self.order_table[order.init_id] = order
        self._save_state()
        return order.strategy_name

    def fill_order(self, strategy_name, order_number, quantity, return_order=False):
        for _, order in self.order_table.items():
            if (strategy_name == order.strategy_name) and \
                    (order.state == 'open') and \
                        (order_number == order.order_number):
                filled = order.fill_order(quantity, return_filled=True)
                if filled:
                    self.clean_filled_orders()
                self._save_state()
                if return_order:
                    return order

    def clean_filled_orders(self):
        """
        order 상태가 filled인 경우 딕셔너리에서 제거
        """
        to_pop = []
        for init_id, order in self.order_table.items():
            if order.state == OrderState.FILLED:
                to_pop.append(init_id)
        for init_id in to_pop:
            self.order_table.pop(init_id)
        self._save_state()

    def get_strategy_orders(self,
                            strategy_name,
                            states: list = [OrderState.INIT, OrderState.OPEN, OrderState.FILLED]):
        orders = []
        for _, order in self.order_table.items():
            if (order.strategy_name == strategy_name) and (order.state in states):
                orders.append(order)
        return orders


if __name__ == '__main__':
    from order.api import Order

    # o = Order('strategy', 'symbol', 1, 100, 'LONG', 'LIMIT', '신한')
    # oo = Order('strategy', 'symbol', 1, 100, 'LONG', 'LIMIT', '신한')

    ot = OrderTable()
    # ot.add_order(o)
    # ot.add_order(oo)

    orders = ot.get_strategy_orders('strategy', [OrderState.FILLED])
    print(ot)
