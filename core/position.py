import datetime


class PositionState:
    OPEN = 'open'
    CLOSED = 'closed'


class Position:

    def __init__(self, strategy_name, symbol):
        self.POSITION_STATE = PositionState.CLOSED
        self.strategy_name = strategy_name
        self.symbol = symbol

    def calculate_average_price(self):
        pq, q = 0, 0
        for i in range(len(self.trade_history)):
            if self.trade_history[i] == 'ENTER':
                pq += self.price_history[i] * self.quantity_history[i]
                q += self.quantity_history[i]
        return pq / q

    def open_position(self, side, price, quantity, position_amount):
        self.POSITION_STATE = PositionState.OPEN
        self.position_open_date = datetime.datetime.now().strftime('%Y%m%d')
        self.side = side if side is not None else ''                                      # BUY / SELL
        self.average_price = price if price is not None else 0                            # 평균단가 (주식/계약 가격)
        self.quantity = quantity if quantity is not None else 0                           # 투자수량
        self.position_amount = position_amount if position_amount is not None else 0      # 투자금액
        try:
            self.leverage = abs((price * quantity) / position_amount)  # (평균단가 * 투자수량) / 투자금액
        except:
            self.leverage = 1

        self.price_history = [price] if price is not None else []
        self.quantity_history = [quantity] if quantity is not None else []
        self.trade_history = ['ENTER'] if quantity is not None else []

    def update_position(self, price, quantity, position_amount=None):
        """
        quantity, amount는 +/- 모두 가능
        """
        self.price_history.append(price)
        self.quantity_history.append(quantity)

        self.quantity += quantity
        if position_amount is None:
            self.position_amount += (price * quantity)
        else:
            self.position_amount += position_amount

        if self.side == 'BUY':
            if quantity > 0:
                trade_position = 'ENTER'
            else:
                trade_position = 'EXIT'

        if self.side == 'SELL':
            if quantity < 0:
                trade_position = 'ENTER'
            else:
                trade_position = 'EXIT'

        self.trade_history.append(trade_position)
        self.average_price = self.calculate_average_price()

        self.leverage = abs((self.average_price * self.quantity) / self.position_amount)
        self.close_position()

    def close_position(self):
        init_condition_1 = (self.quantity == 0) and (len(self.quantity_history) != 0)
        init_condition_2 = (self.POSITION_STATE == PositionState.CLOSED)

        if init_condition_1 or init_condition_2:
            self.POSITION_STATE = PositionState.CLOSED
            self.position_open_date = datetime.datetime.now().strftime('%Y%m%d')
            self.side = ''
            self.average_price = 0
            self.quantity = 0
            self.position_amount = 0
            self.leverage = 0

            self.price_history = []
            self.quantity_history = []
            self.trade_history = []

    @property
    def position_enter_cnt(self):
        return self.trade_history.count('ENTER')

    @property
    def position_exit_cnt(self):
        return self.trade_history.count('EXIT')


if __name__ == '__main__':
    p = Position('name', 'symbol')
    p.open_position(side='BUY', price=100, quantity=1, position_amount=-100)
    print(p.__dict__)
    p.update_position(price=110, quantity=3, position_amount=-330)
    print(p.__dict__)
    p.update_position(price=120, quantity=-1, position_amount=120)
    print(p.__dict__)

    print(p)