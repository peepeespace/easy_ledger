import numpy as np


class Position:

    def __init__(self, strategy_name, symbol, side, price=None, quantity=None, position_amount=None):
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.side = side                                      # LONG / SHORT
        self.average_price = price                            # 평균단가 (주식/계약 가격)
        self.quantity = quantity                              # 투자수량
        self.position_amount = position_amount                # 투자금액
        self.leverage = (price * quantity) / position_amount  # (평균단가 * 투자수량) / 투자금액

        self.price_history = [price]
        self.quantity_history = [quantity]
        self.trade_history = ['ENTER']

    def update_position(self, quantity, price, amount):
        """
        quantity, amount는 +/- 모두 가능
        """
        self.price_history.append(price)
        self.quantity_history.append(quantity)

        self.quantity += quantity
        self.position_amount += amount
        self.average_price = (np.array(self.price_history) * np.array(self.quantity_history)).mean()
        self.leverage = (self.average_price * self.quantity) / self.position_amount

        if self.side == 'LONG':
            if quantity > 0:
                self.trade_history.append('ENTER')
            else:
                self.trade_history.append('EXIT')

        if self.side == 'SHORT':
            if quantity < 0:
                self.trade_history.append('ENTER')
            else:
                self.trade_history.append('EXIT')

    def __dict__(self):
        return {
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'side': self.side,
            'average_price': self.average_price,
            'quantity': self.quantity,
            'position_amount': self.position_amount,
            'price_history': self.price_history,
            'quantity_history': self.quantity_history
        }

    @property
    def position_enter_cnt(self):
        return self.trade_history.count('ENTER')

    @property
    def position_exit_cnt(self):
        return self.trade_history.count('EXIT')


class PositionPool:

    def __init__(self):
        """
        pool은 strategy별 position을 관리해주는 딕셔너리

        pool --> {
            'strategy_1': {'code_1': {'LONG': position_1, 'SHORT': position_2}, ... },
            'strategy_2': {'code_2': {'SHORT': position_2}},
            ...
        }
        """
        self.pool = {}

    def add_to_pool(self, position):
        strategy_name = position.strategy_name
        symbol = position.symbol
        side = position.side

        if strategy_name not in self.pool:
            self.pool[strategy_name] = {}

        if symbol not in self.pool[strategy_name]:
            self.pool[strategy_name][symbol] = {}

        if side not in self.pool[strategy_name][symbol]:
            self.pool[strategy_name][symbol][side] = position

    def get_position(self, strategy_name, symbol, side):
        return self.pool.get(strategy_name, {}).get(symbol, {}).get(side)


if __name__ == '__main__':
    p = Position('name', 'symbol', 'LONG', 1, 100, 100)
    print(p.__dict__())