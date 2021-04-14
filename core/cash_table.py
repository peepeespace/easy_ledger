import os
import pickle


class CashTable:

    CACHE_NAME = 'CashTable.pkl'

    def __init__(self):
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.CACHE_NAME):
            f = open(self.CACHE_NAME, 'rb')
            cached = pickle.load(f)
            self.cash_table = cached.cash_table
        else:
            self.cash_table = {}
            self._save_state()

    def _save_state(self):
        with open(self.CACHE_NAME, 'wb') as f:
            pickle.dump(self, f)

    def get_cash(self, strategy_name, meta=None):
        if strategy_name not in self.cash_table:
            self.cash_table[strategy_name] = {}

        if meta is None:
            return self.cash_table[strategy_name]
        else:
            return self.cash_table[strategy_name].get(meta, 0)

    def update_cash(self, strategy_name, amount, meta=None):
        cash_info = self.get_cash(strategy_name)

        if meta is None:
            cash_info['cash'] = amount
        else:
            cash_info[meta] = amount

        self._save_state()