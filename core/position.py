import datetime

from core.order import OrderState


class PositionState:
    OPEN = 'open'
    CLOSED = 'closed'


class Position:

    def __init__(self, strategy_name: str, symbol: str, meta: str = None):
        self.POSITION_STATE = PositionState.CLOSED
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.meta = meta

    @classmethod
    def update_average_price(self,
                             prev_average_price: float,
                             prev_quantity: float,
                             price: float,
                             quantity: float):
        """
        *== 평균단가 계산 예시 ==*

        price | quantity | prev_average_price | average_price                                    | total_quantity
        100     +1         0                    ((0 * 0) + (100 * 1)) / (0 + 1) = 100              1
        110     +2         100                  ((100 * 1) + (110 * 2)) / (1 + 2) = 106.66         3
        105     -1         106.66               ((106.66 * 3) + (106.66 * -1)) / (3 - 1) = 106.66  2
        90      +3         106.66               ((106.66 * 2) + (90 * 3)) / (2 + 3) = 96.664       5

        --> ENTER를 하는 경우 price/quantity에 모두 영향을 미치고,
            EXIT을 하는 경우 quantity에만 영향을 미친다.
        """

        if quantity >= 0:
            p = price
        else:
            p = prev_average_price

        numerator = ((prev_average_price * prev_quantity) + (p * quantity))
        denominator = prev_quantity + quantity

        if denominator == 0.0:
            return 0.0
        else:
            return numerator / denominator

    def open_position(self,
                      side: str = None,
                      price: float = None,
                      quantity: float = None,
                      position_amount: float = None,
                      order_state: OrderState = None):
        """
        
        :param side: BUY / SELL
        :param price: float --> 소수점으로 매매가 가능한 자산군도 존재하기 때문
        :param quantity: float --> 소수점으로 매매가 가능한 자산군도 존재하기 때문
        :param position_amount: 실제 투자 금액 (레버리지를 사용하는 경우)
        :param order_state: None / 'filled' --> filled인 경우 n차 매매로 기록 (분할 매수/매도에 필요한 정보)
        :return: 
        """

        self.POSITION_STATE = PositionState.OPEN
        self.position_open_date = datetime.datetime.now().strftime('%Y%m%d')
        self.side = side if side is not None else ''                                      # BUY / SELL
        self.average_price = price if price is not None else 0.0                          # 평균단가 (주식/계약 가격)
        self.quantity = quantity if quantity is not None else 0.0                         # 투자수량
        self.position_amount = position_amount if position_amount is not None else 0.0    # 투자금액
        try:
            self.leverage = abs((price * quantity) / position_amount)  # (평균단가 * 투자수량) / 투자금액
        except:
            self.leverage = 1.0

        self.price_history = [price] if price is not None else []
        self.quantity_history = [quantity] if quantity is not None else []
        self.trade_history = ['ENTER'] if quantity is not None else []
        self.fill_history = [order_state == OrderState.FILLED] # 몇차 거래인지 파악하기 위한 수단

    def update_position(self,
                        price: float = 0.0,
                        quantity: float = 0.0,
                        position_amount: float = None,
                        order_state: str = None):
        """
        quantity, amount는 +/- 모두 가능

        실제로 fill된 주문에 대해서만 fill_history에 기록한다. (체결완료 / 주문취소 두가지 경우에 가능)
        """
        self.price_history.append(price)
        self.quantity_history.append(quantity)
        self.fill_history.append(order_state == OrderState.FILLED)

        self.average_price = self.update_average_price(prev_average_price=self.average_price,
                                                       prev_quantity=self.quantity,
                                                       price=price,
                                                       quantity=quantity)

        self.quantity += quantity
        if position_amount is None:
            amount = price * quantity
            if self.side == 'SELL':
                amount = -1 * amount
            self.position_amount += amount
        else:
            self.position_amount += position_amount

        if self.side == 'BUY':
            if quantity > 0.0:
                trade_position = 'ENTER'
            elif quantity == 0.0:
                trade_position = 'CANCEL'
            else:
                trade_position = 'EXIT'

        if self.side == 'SELL':
            if quantity < 0.0:
                trade_position = 'ENTER'
            elif quantity == 0.0:
                trade_position = 'CANCEL'
            else:
                trade_position = 'EXIT'

        self.trade_history.append(trade_position)

        try:
            self.leverage = abs((self.average_price * self.quantity) / self.position_amount)
        except:
            self.leverage = 0

        self.close_position()

    def close_position(self):
        """
        매매가 종료된 시점에서 position을 닫아주고, 다른 side를 취할 수 있도록 해준다.
        """
        init_condition_1 = (self.quantity == 0) and (len(self.quantity_history) != 0)
        init_condition_2 = (self.POSITION_STATE == PositionState.CLOSED)

        if init_condition_1 or init_condition_2:
            self.POSITION_STATE = PositionState.CLOSED
            self.position_open_date = datetime.datetime.now().strftime('%Y%m%d')
            self.side = ''
            self.average_price = 0.0
            self.quantity = 0.0
            self.position_amount = 0.0
            self.leverage = 0.0

            self.price_history = []
            self.quantity_history = []
            self.trade_history = []
            self.fill_history = []

    @property
    def position_enter_cnt(self):
        return self.trade_history.count('ENTER')

    @property
    def position_exit_cnt(self):
        return self.trade_history.count('EXIT')

    @property
    def fill_cnt(self):
        """
        fill_cnt가 필요한 이유는: 한 주문에 대해서 여러번에 걸쳐서 체결이 되는 경우 한번의 거래로 보기 때문이다.
        여러번 체결을 하였더라도 같은 주문에 대한 체결이면 fill_cnt로 정확히 몇번의 주문을 통해서 position이 생긴건지
        파악하기 위해서 필요하다.
        """
        try:
            return self.fill_history.count(True)
        except:
            return 0


if __name__ == '__main__':
    p = Position('name', 'symbol')
    p.open_position(side='BUY', price=100, quantity=1, position_amount=-100)
    print(p.__dict__)
    p.update_position(price=110, quantity=3, position_amount=-330)
    print(p.__dict__)
    p.update_position(price=120, quantity=-1, position_amount=120)
    print(p.__dict__)

    print(p)