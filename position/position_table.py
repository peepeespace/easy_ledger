import os
import pickle

from .api import Position, PositionState


class PositionTable:

    CACHE_NAME = 'PositionTable.pkl'

    def __init__(self):
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.CACHE_NAME):
            f = open(self.CACHE_NAME, 'rb')
            cached = pickle.load(f)
            self.position_table = cached.position_table
        else:
            self.position_table = {}
            self._save_state()

    def _save_state(self):
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

    def update_position(self, strategy_name, symbol, side, price, quantity, position_amount):
        position = self.get_position(strategy_name, symbol)
        if position.POSITION_STATE == PositionState.CLOSED:
            position.open_position(side=side, price=price, quantity=quantity, position_amount=position_amount)
        else:
            position.update_position(price=price, quantity=quantity, position_amount=position_amount)
        self._save_state()