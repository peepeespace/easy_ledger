import os
import pickle
from typing import List
from pathlib import Path

from core.order import Order, OrderState


class OrderTable:
    """
    Order 관련된 meta 데이터를 저장하기 위한 수단
    예를 들어서 동일한 종류의 주문을 어떤 전략들이 현재 넣은 상태인지 등

    hash값이 같은 경우도 발생할 수 있기 때문에 (다른 전략이 같은 종류의 주문을 연속해서 넣는 경우)
    equal_orders 같은 meta 데이터로 이를 관리한다.
    """

    CACHE_NAME = 'OrderTable.pkl'

    def __init__(self, user_name='', ledger_name='', auto_save=False):
        path = Path.home() / 'easy_ledger' / user_name / ledger_name
        path.mkdir(parents=True, exist_ok=True)
        self.CACHE_NAME = path / self.CACHE_NAME
        self.auto_save = auto_save
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.CACHE_NAME) and self.auto_save:
            f = open(self.CACHE_NAME, 'rb')
            cached = pickle.load(f)
            self.order_table = cached.order_table
            self.order_meta = cached.order_meta
        else:
            self.order_table = {}
            self.order_meta = {}
            self._save_state()

    def _save_state(self):
        if self.auto_save:
            with open(self.CACHE_NAME, 'wb') as f:
                pickle.dump(self, f)

    def add_order(self, order: Order):
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

    def remove_order(self, order_number: str, strategy_name: str = None):
        to_del = []
        for init_id, order in self.order_table.items():
            # Condition #1: init 상태가 아닌 주문에 대해서만 적용 (order_number이 필요하기 때문)
            order_state_condition = (order.ORDER_STATE != OrderState.INIT)

            if order_state_condition:
                # Condition #2: 주문 번호가 일치하는지 확인
                order_number_condition = (order.order_number == order_number)

                # Condition #3: strategy_name이 일치하는지 확인
                if strategy_name is not None:
                    strategy_name_condition = (order.strategy_name == strategy_name)
                else:
                    strategy_name_condition = True

                if order_number_condition and strategy_name_condition:
                    order.make_closed_order()
                    to_del.append(init_id)

        cancelled_orders = []
        for id in to_del:
            cancelled_orders.append(self.order_table.pop(id))

        self._save_state()

        return cancelled_orders

    def register_order(self, order_hash):
        """
        add된 order를 실제 주문 거래소(소스)에서 접수가 완료된 것을 확인한 후 register된 order를 리턴하는 역할

        먼저 주문을 init한 전략의 주문이 먼저 체결된다는 가정하에 먼저 등록된 order를 pop하여 리턴한다.
        """
        try:
            order = self.order_meta[order_hash]['equal_orders'].pop()
            if not self.order_meta[order_hash]['equal_orders']: # 더 이상 이 주문이 접수되길 대기하는 전략이 없다면 제거
                del self.order_meta[order_hash]
            self._save_state()
            return order
        except:
            return

    def make_open_order(self, order_hash, order_number):
        # 주문을 접수시킴과 동시에 미체결 상태로 전환
        order = self.register_order(order_hash)
        if order is not None:
            order.make_open_order(order_number)
            self.order_table[order.init_id] = order
        self._save_state()
        return order

    def fill_order(self, strategy_name, order_number, quantity, return_order=False):
        for _, order in self.order_table.items():
            if (strategy_name == order.strategy_name) and \
                    (order.state == OrderState.OPEN) and \
                        (order_number == order.order_number):
                try:
                    filled = order.fill_order(quantity, return_filled=True)
                except:
                    # 주문 수량보다 많은 수량을 체결시키려 하면 오류 발생
                    filled = False

                if filled:
                    self.clean_filled_orders()
                self._save_state()
                if return_order:
                    return order

    def clean_orders(self, state: OrderState, strategy_name: str = None):
        """
        주문 상태에 따라 필터하여 제거하는 함수
        전략 이름을 인자값으로 넣었다면 strategy로 한번 더 필터링하여 주문 제거/정리
        """
        to_pop = []
        for init_id, order in self.order_table.items():
            state_condition = (order.state == state)
            if strategy_name is not None:
                strategy_name_condition = (order.strategy_name == strategy_name)
            else:
                strategy_name_condition = True

            if state_condition and strategy_name_condition:
                to_pop.append(init_id)

        for init_id in to_pop:
            self.order_table.pop(init_id)
        self._save_state()

    def clean_init_orders(self, strategy_name: str = None):
        self.clean_orders(state=OrderState.INIT, strategy_name=strategy_name)

    def clean_open_orders(self, strategy_name: str = None):
        self.clean_orders(state=OrderState.OPEN, strategy_name=strategy_name)

    def clean_filled_orders(self, strategy_name: str = None):
        self.clean_orders(state=OrderState.FILLED, strategy_name=strategy_name)

    def clean_closed_orders(self, strategy_name: str = None):
        self.clean_orders(state=OrderState.CLOSED, strategy_name=strategy_name)

    def get_orders(self,
                   strategy_name: str,
                   states: list = [OrderState.INIT, OrderState.OPEN, OrderState.FILLED]) -> List[Order]:
        orders = []
        for _, order in self.order_table.items():
            if (order.strategy_name == strategy_name) and (order.state in states):
                orders.append(order)
        return orders

    def get_order(self, strategy_name: str, order_number: str) -> Order:
        for _, order in self.order_table.items():
            if order.ORDER_STATE != OrderState.INIT:
                # ORDER_STATE가 init이면 order_number가 없기 때문에 오류가 발생한다. (오류 방지)
                if (order.strategy_name == strategy_name) and (order.order_number == order_number):
                    return order


if __name__ == '__main__':
    from core.order import Order

    # o = Order('strategy', 'symbol', 1, 100, 'LONG', 'LIMIT', '신한')
    # oo = Order('strategy', 'symbol', 1, 100, 'LONG', 'LIMIT', '신한')

    ot = OrderTable()
    # ot.add_order(o)
    # ot.add_order(oo)

    orders = ot.get_orders('strategy', [OrderState.FILLED])
    print(ot)
