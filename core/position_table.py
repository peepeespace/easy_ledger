import os
import pickle
from pathlib import Path

from .position import Position, PositionState


class PositionTable:

    CACHE_NAME = 'PositionTable.pkl'

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
            self.position_table = cached.position_table
        else:
            self.position_table = {}
            self._save_state()

    def _save_state(self):
        if self.auto_save:
            with open(self.CACHE_NAME, 'wb') as f:
                pickle.dump(self, f)

    def get_positions(self, strategy_name):
        if strategy_name not in self.position_table:
            self.position_table[strategy_name] = {}

        return self.position_table[strategy_name]

    def get_position(self, strategy_name, symbol):
        positions = self.get_positions(strategy_name)

        if symbol not in positions:
            positions[symbol] = Position(strategy_name=strategy_name, symbol=symbol)

        return positions[symbol]

    def update_position(self, strategy_name, symbol, side, price, quantity, position_amount, order_state=None):
        position = self.get_position(strategy_name, symbol)
        if position.POSITION_STATE == PositionState.CLOSED:
            position.open_position(side=side, price=price, quantity=quantity,
                                   position_amount=position_amount, order_state=order_state)
        else:
            position.update_position(price=price, quantity=quantity, position_amount=position_amount,
                                     order_state=order_state)
        self._save_state()