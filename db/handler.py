from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from db.models import Strategy, Order, Fill


class DBHandler:

    DATABASE_URL = "sqlite:///./ledger.db"

    def __init__(self):
        self.engine = create_engine(
            self.DATABASE_URL, connect_args={"check_same_thread": False}
        )
        self.base = declarative_base()
        self.base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
        self.session = self.Session()

    # ** Strategy ** #
    def create_strategy(self, name: str):
        query = self.session.query(Strategy).filter(Strategy.name == name)
        if query.count() == 0:
            strategy = Strategy(name=name)
            self.session.add(strategy)
            self.session.commit()
        else:
            strategy = query.one()
        return strategy

    def get_strategy(self, name: str):
        return self.create_strategy(name=name)

    def get_strategies(self):
        return self.session.query(Strategy).all()

    def get_strategy_by_id(self, id: int):
        return self.session.query(Strategy).filter(Strategy.id == id).one()

    def update_strategy(self, id: int, **params) -> int:
        strategy = self.get_strategy_by_id(id=id)
        for field, value in params.items():
            try:
                setattr(strategy, field, value)
            except:
                print(f'{strategy} has no {field} field')
        self.session.commit()
        return id

    def delete_strategy(self, id: int) -> int:
        strategy = self.get_strategy_by_id(id=id)
        self.session.delete(strategy)
        self.session.commit()
        return id

    # ** Order ** #
    def create_order(self, strategy_name: str, symbol: str, price: int or float, quantity: int or float,
                     side: str, order_type: str, meta: str = None):
        order = Order(
            strategy_name=strategy_name,
            symbol=symbol,
            price=price,
            quantity=quantity,
            side=side,
            order_type=order_type,
            meta=meta
        )
        self.session.add(order)
        self.session.commit()
        return order

    def get_order(self, id: int):
        return self.session.query(Order).filter(Order.id == id).one()

    def get_orders(self, strategy_name: str = None):
        query = self.session.query(Order)
        if strategy_name is not None:
            strategy = self.get_strategy(name=strategy_name)
            orders = query.filter(Order.strategy_id == strategy.id).all()
        else:
            orders = query.all()
        return orders

    def update_order(self, id: int, **params):
        order = self.get_order(id=id)
        for field, value in params.items():
            try:
                setattr(order, field, value)
            except:
                print(f'{order} has no {field} field')
        self.session.commit()
        return id

    def delete_order(self, id: int):
        order = self.get_order(id=id)
        self.session.delete(order)
        self.session.commit()
        return id

    # ** Fill ** #
    def create_fill(self, order_id: int, timestamp: str, quantity: int or float, price: int or float = None):
        fill = Fill(
            order_id=order_id,
            timestamp=timestamp,
            quantity=quantity,
            price=price
        )
        self.session.add(fill)
        self.session.commit()
        return fill

    def get_fill(self, id: int):
        return self.session.query(Fill).filter(Fill.id == id).one()

    def get_fills(self, order_id: int):
        return self.session.query(Fill).filter(Fill.order_id == order_id).all()

    def update_fill(self, id: int, **params):
        fill = self.get_fill(id=id)
        for field, value in params.items():
            try:
                setattr(fill, field, value)
            except:
                print(f'{fill} has no {field} field')
        self.session.commit()
        return id

    def delete_fill(self, id: int):
        fill = self.get_fill(id=id)
        self.session.delete(fill)
        self.session.commit()
        return id


if __name__ == '__main__':
    db = DBHandler()

    st = db.get_strategy('alsidnfaf')
    print(st)