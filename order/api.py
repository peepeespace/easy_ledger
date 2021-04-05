import os
import json
import pickle
import hashlib
import datetime

CACHE_DIR = '.\\order_cache'

class OrderState:
    INIT = 'init'
    OPEN = 'open'
    FILLED = 'filled'


class Order:
    """
    주문 프로세스에 따라서 Order의 상태가 변하게 된다.

    init --> open --> filled

    상태가 변할때마다 사용할 수 있는 property의 수가 늘어난다.
    """

    def __init__(self, strategy_name, symbol, price, quantity, side, order_type, meta=None):
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)

        self.ORDER_STATE = OrderState.INIT
        self.init_time = self._time()

        self.strategy_name = strategy_name
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.side = side
        self.order_type = order_type
        self.meta = meta

        self.hash = self.make_order_hash(symbol=symbol,
                                         quantity=quantity,
                                         price=price,
                                         side=side,
                                         order_type=order_type,
                                         meta=meta)

        # state별 id값
        self.init_id = None
        self.open_id = None
        self.filled_id = None

        self.init_id = self.id
        self._save_state()

    def _save_state(self):
        filename = f'{CACHE_DIR}\\order_{self.init_id}.pkl'
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    def _time(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]

    @classmethod
    def make_order_hash(self, symbol, price, quantity, side, order_type, meta):
        """
        모든 주문을 잘 구분하기 위한 요소만 사용하여 hash를 한다.
        주문에 대한 모든 정보는 OrderHash 객체로 관리하는 것이 편리하다.
        주문을 추가하고 제거하는 작업은 hash를 통해서도 충분하다.

        meta 인자를 넣어줌으로써 같은 형식의 주문과 차이를 줄 수 있다. (거래소/자산군 등과 같은 정보)
        """
        self.order_base_info = {
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'side': side,
            'order_type': order_type,
            'meta': meta
        }
        order_info_string = f'{symbol} {price} {quantity} {side} {order_type} {meta}'
        return hashlib.sha1(order_info_string.encode('utf-8')).hexdigest()

    def make_open_order(self, order_number):
        self.ORDER_STATE = OrderState.OPEN
        self.open_time = self._time()

        self.order_number = order_number
        self.orders_filled = 0
        self.orders_remaining = self.quantity
        self.fill_history = []

        # property를 모두 업데이트하고 state의 id 부여하기
        self.open_id = self.id
        self._save_state()

    def make_filled_order(self):
        self.ORDER_STATE = OrderState.FILLED
        self.filled_time = self._time()

        # property를 모두 업데이트하고 state의 id 부여하기
        self.filled_id = self.id
        self._save_state()

    def fill_order(self, quantity, return_filled=False):
        if quantity > self.orders_remaining:
            raise Exception('체결 수량이 남은 수량보다 클 수 없습니다. 다시 확인바랍니다.')
        self.orders_filled += quantity
        self.orders_remaining -= quantity
        self.fill_history.append({'timestamp': self._time(), 'quantity': quantity})
        self._save_state()

        if self.filled:
            self.make_filled_order()

        if return_filled:
            return self.filled

    @property
    def id(self):
        # 객체 고유 이름 (주문 hash와는 다른 용도)
        state = self.state
        id = getattr(self, f'{state}_id')
        if id is None:
            return hashlib.sha1(json.dumps(self.__dict__).encode('utf-8')).hexdigest()
        else:
            return id

    @property
    def state(self):
        return self.ORDER_STATE

    @property
    def filled(self):
        if self.orders_remaining == 0:
            return True
        else:
            return False


def load_cached_order(order_init_id):
    with open(f'{CACHE_DIR}\\order_{order_init_id}.pkl', 'rb') as f:
        order = pickle.load(f)
    return order


if __name__ == '__main__':
    o = Order('strategy', 'symbol', 1, 100, 'BUY', 'LIMIT', '신한')
    print(o.state)
    print(o.__dict__)

    print(o.id)

    o.make_open_order('123123')
    print(o.state)
    print(o.__dict__)

    print(o.id)

    filled = o.fill_order(0.5, return_filled=True)
    if filled:
        o.make_filled_order()

    filled = o.fill_order(0.5, return_filled=True)
    if filled:
        o.make_filled_order()

    print(o.state)
    print(o.__dict__)

    print(o.id)


    order_init_id = o.init_id

    order = load_cached_order(order_init_id)
    print(order)

