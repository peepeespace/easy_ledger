import datetime

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
        Ledger,
        Strategy,
        Cash,
        Order,
        Fill,
        Position,
        Universe,
    )

    DB_AVAILABLE = True
except:
    DB_AVAILABLE = False


class LedgerDB:

    def __init__(self, name=None, username=None, db_save=False):
        self.name = name
        self.username = username
        self.db_save = db_save

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

            ledger = Ledger.objects.filter(user=self.user, name=self.name).first()
            if ledger is None:
                self.db = Ledger(user=self.user, name=self.name)
                self.db.save()
            else:
                self.db = ledger

    def update_cash_db(self, strategy_name, amount, quote='krw'):
        if self.db_save:
            cash = Cash.objects.get_or_create(user=self.user,
                                              strategy_name=strategy_name,
                                              quote=quote)[0]
            cash.amount = amount
            cash.save()

    def init_order_db(self, order):
        if self.db_save:
            order_instance = Order(user=self.user,
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

    def register_order_db(self, order):
        if self.db_save:
            o = Order.objects.filter(user=self.user,
                                     strategy_name=order.strategy_name,
                                     init_id=order.init_id).first()
            o.order_state = order.ORDER_STATE
            o.order_number = order.order_number
            o.open_id = order.open_id
            o.open_time = order.open_time
            o.orders_filled = order.orders_filled
            o.orders_remaining = order.orders_remaining
            o.save()

    def cancel_order_db(self, order):
        if self.db_save:
            o = Order.objects.filter(user=self.user,
                                     strategy_name=order.strategy_name,
                                     init_id=order.init_id).first()
            o.order_state = order.ORDER_STATE
            o.closed_id = order.closed_id
            o.closed_time = order.closed_time
            o.save()

    def fill_order_db(self, order, price):
        if self.db_save:
            o = Order.objects.filter(user=self.user,
                                     strategy_name=order.strategy_name,
                                     init_id=order.init_id).first()
            o.order_state = order.ORDER_STATE
            o.filled_id = order.filled_id
            o.filled_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
            o.orders_filled = order.orders_filled
            o.orders_remaining = order.orders_remaining
            o.save()

            fill_history = order.fill_history

            if fill_history:
                fill = fill_history[-1]
                f = Fill(order=o,
                         timestamp=fill['timestamp'],
                         quantity=fill['quantity'],
                         price=price)
                f.save()