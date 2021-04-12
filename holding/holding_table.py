import os
import pickle


class HoldingTable:

    CACHE_NAME = 'HoldingTable.pkl'

    def __init__(self):
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.CACHE_NAME):
            f = open(self.CACHE_NAME, 'rb')
            cached = pickle.load(f)
            self.holding_table = cached.holding_table
        else:
            self.holding_table = {}
            self._save_state()

    def _save_state(self):
        with open(self.CACHE_NAME, 'wb') as f:
            pickle.dump(self, f)

    def get_holdings(self, strategy_name):
        if strategy_name not in self.holding_table:
            self.holding_table[strategy_name] = {}

        return self.holding_table[strategy_name]

    def get_holding(self, strategy_name, field):
        holdings = self.get_holdings(strategy_name)

        if field not in holdings:
            holdings[field] = None

        return holdings[field]

    def update_holding(self, strategy_name, field, amount):
        _ = self.get_holding(strategy_name, field)
        self.holding_table[strategy_name][field] = amount
        self._save_state()