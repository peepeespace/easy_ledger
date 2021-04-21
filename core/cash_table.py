import os
import pickle
from pathlib import Path


class CashTable:

    CACHE_NAME = 'CashTable.pkl'

    def __init__(self, ledger_name='', auto_save=False):
        path = Path.home() / 'easy_ledger' / ledger_name
        path.mkdir(parents=True, exist_ok=True)
        self.CACHE_NAME = path / self.CACHE_NAME
        self.auto_save = auto_save
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.CACHE_NAME) and self.auto_save:
            f = open(self.CACHE_NAME, 'rb')
            cached = pickle.load(f)
            self.cash_table = cached.cash_table
        else:
            self.cash_table = {}
            self._save_state()

    def _save_state(self):
        if self.auto_save:
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


if __name__ == '__main__':
    ct = CashTable(auto_save=True)
    cash = ct.get_cash('strategy_1')
    print(cash)