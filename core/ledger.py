import uuid

from core.order import Order
from core.cash_table import CashTable
from core.order_table import OrderTable
from core.position_table import PositionTable

try:
    """
    Django 관련 모듈이 있다면 DB에 데이터를 저장하여 Ledger 데이터를 persist할 수 있다.
    """
    import os
    from django.contrib.auth import authenticate
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
    application = get_wsgi_application()

    from user.models import User, UserProfile
    from db.models import (
        Ledger as LedgerModel,
        Strategy as StrategyModel,
        Order as OrderModel,
        Fill as FillModel,
        Position as PositionModel,
        Universe as UniverseModel,
    )

    DB_AVAILABLE = True
except:
    DB_AVAILABLE = False


class Ledger:
    """
    Ledger는 원장이라는 뜻이며, 프로그램 상에서 발생하는 모든 액션을 기록하는 목적을 가지고 있다.

    실제 주문 발생과 같은 역할은 모두 외부에서 발생시키며, 원장은 철저히 데이터 관리에만 집중한다.
    """

    def __init__(self,
                 name=str(uuid.uuid1()),
                 username=None,
                 auto_save=False,
                 db_save=False):
        # auto_save: pkl파일로 각 table의 상태를 저장
        # db_save: 모든 transaction을 DB에 저장
        self.name = name            # Ledger 이름
        self.username = username    # DB 유저 이름

        self.cash_table = CashTable(name, auto_save)
        self.order_table = OrderTable(name, auto_save)
        self.position_table = PositionTable(name, auto_save)

        self.db_save = (DB_AVAILABLE and db_save)
        self.sync_db()

    def sync_db(self):
        if self.db_save:
            if self.username is None:
                self.username = input('[Ledger] Enter Email: ')
            self.user = User.objects.filter(email=self.username).first()
            if self.user is None:
                print('[Ledger] No such user. Creating new user...')
                password = input('[Ledger] Enter New Password: ')
                self.user = User(username=self.username, email=self.username, password=password)
                self.user.save()

            ledger = LedgerModel.objects.filter(name=self.name).first()
            if ledger is None:
                self.db = LedgerModel(user=self.user, name=self.name)
                self.db.save()
            else:
                self.db = ledger

    def add_strategy(self, strategy_name, account_number=None, description=None):
        strategy = StrategyModel(ledger=self.db,
                                 name=strategy_name,
                                 account_number=account_number,
                                 description=description)
        strategy.save()
        return strategy

    def get_strategy(self, strategy_name):
        strategy = StrategyModel.objects.filter(ledger=self.db, name=strategy_name).first()
        if strategy is None:
            return self.add_strategy(strategy_name=strategy_name)
        else:
            return strategy

    def order_hash(self, symbol, price, quantity, side, order_type, quote, meta):
        return Order.make_order_hash(symbol=symbol,
                                     price=price,
                                     quantity=quantity,
                                     side=side,
                                     order_type=order_type,
                                     quote=quote,
                                     meta=meta)

    def get_cash(self, strategy_name, quote=None):
        return self.cash_table.get_cash(strategy_name=strategy_name, quote=quote)

    def update_cash(self, strategy_name, amount, quote=None):
        self.cash_table.update_cash(strategy_name=strategy_name, amount=amount, quote=quote)

    def get_orders(self, strategy_name):
        return self.order_table.get_orders(strategy_name=strategy_name)

    def get_order(self, strategy_name, order_number, format='dict'):
        order = self.order_table.get_order(strategy_name=strategy_name, order_number=order_number)
        if order is not None:
            if format == 'dict':
                return order.__dict__
            else:
                return order

    def clean_orders(self, state, strategy_name=None):
        self.order_table.clean_orders(state=state, strategy_name=strategy_name)

    def get_positions(self, strategy_name):
        return self.position_table.get_positions(strategy_name=strategy_name)

    def get_position(self, strategy_name, symbol, format='dict'):
        position = self.position_table.get_position(strategy_name=strategy_name, symbol=symbol)
        if format == 'dict':
            return position.__dict__
        else:
            return position

    def update_position(self, strategy_name, symbol, side, price, quantity, position_amount=None, order_state=None):
        self.position_table.update_position(strategy_name=strategy_name,
                                            symbol=symbol,
                                            side=side,
                                            price=price,
                                            quantity=quantity,
                                            position_amount=position_amount,
                                            order_state=order_state)

    def init_order(self, strategy_name, symbol, price, quantity, side, order_type, quote=None, meta=None):
        order = Order(strategy_name=strategy_name,
                      symbol=symbol,
                      price=price,
                      quantity=quantity,
                      side=side,
                      order_type=order_type,
                      quote=quote,
                      meta=meta)
        self.order_table.add_order(order)
        if self.db_save:
            order_instance = OrderModel(user=self.user,
                                        strategy_name=order.strategy_name,
                                        order_state=order.ORDER_STATE,
                                        init_time=order.init_time,
                                        symbol=order.symbol,
                                        quantity=order.quantity,
                                        price=order.price,
                                        side=order.side,
                                        order_type=order.order_type,
                                        quote=order.quote,
                                        meta=order.meta,
                                        hash=order.hash,
                                        init_id=order.init_id)
            order_instance.save()
        return order.hash

    def register_order(self, order_number, order_hash):
        order = self.order_table.make_open_order(order_hash=order_hash, order_number=order_number)
        if self.db_save:
            order_instance = OrderModel.objects.filter(user=self.user,
                                                       strategy_name=order.strategy_name,
                                                       init_id=order.init_id).first()
            order_instance.order_state = order.ORDER_STATE
            order_instance.order_number = order.order_number
            order_instance.open_id = order.open_id
            order_instance.open_time = order.open_time
            order_instance.orders_filled = order.orders_filled
            order_instance.orders_remaining = order.orders_remaining
            order_instance.save()
        return order.strategy_name

    def cancel_order(self, strategy_name, order_number):
        orders = self.order_table.remove_order(strategy_name=strategy_name, order_number=order_number)
        for order in orders:
            order_base_info = order.order_base_info
            self.position_table.update_position(strategy_name=strategy_name,
                                                symbol=order_base_info['symbol'],
                                                side=order_base_info['side'],
                                                price=0.0,
                                                quantity=0.0,
                                                position_amount=0.0,
                                                order_state=order.ORDER_STATE)
            if self.db_save:
                order_instance = OrderModel.objects.filter(user=self.user,
                                                           strategy_name=order.strategy_name,
                                                           init_id=order.init_id).first()
                order_instance.order_state = order.ORDER_STATE
                order_instance.closed_id = order.closed_id
                order_instance.closed_time = order.closed_time
                order_instance.save()

    def fill_order(self, strategy_name, order_number, price, quantity, position_amount=None):
        order = self.order_table.fill_order(strategy_name=strategy_name,
                                            order_number=order_number,
                                            quantity=quantity,
                                            return_order=True)
        order_base_info = order.order_base_info
        self.position_table.update_position(strategy_name=strategy_name,
                                            symbol=order_base_info['symbol'],
                                            side=order_base_info['side'],
                                            price=price,
                                            quantity=quantity,
                                            position_amount=position_amount,
                                            order_state=order.ORDER_STATE)


if __name__ == '__main__':
    strategy_name = 'strategy_1'

    ledger = Ledger(username='ppark9553@simpli.kr', db_save=True)

    ledger.update_cash(strategy_name, 'cash', 1000)

    order_params = {
        'strategy_name': strategy_name,
        'symbol': '005930',
        'quantity': 2,
        'price': 100,
        'side': 'BUY',
        'order_type': 'LIMIT',
        'quote': 'KRW',
        'meta': '신한'
    }

    # client(strategy) sends order
    order_hash = ledger.init_order(**order_params)

    order_number = 'ordernumber123'
    # client's order is registered from real exchange (has order number)
    st = ledger.register_order(order_number, order_hash)
    ledger.cancel_order(strategy_name, order_number)

    ledger.fill_order(st, order_number, 100, 1)
    # ledger.fill_order(strategy_name, order_number, 100, 1)

    print(ledger.order_table.order_table)