from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
Base = declarative_base()


class OrderQueue(Base):
    __tablename__ = 'order_queue'

    id = Column(Integer, primary_key=True)
    queue = Column(String, nullable=True)

    def __repr__(self):
        return self.id


class Strategy(Base):
    __tablename__ = 'strategy'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    orders = relationship('Order')


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, ForeignKey('strategy.id'))
    ORDER_STATE = Column(String, nullable=True)
    init_time = Column(String, nullable=True)
    symbol = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    side = Column(String, nullable=True)
    order_type = Column(String, nullable=True)
    meta = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    init_id = Column(String, nullable=True)
    open_id = Column(String, nullable=True)
    filled_id = Column(String, nullable=True)
    open_time = Column(String, nullable=True)
    order_number = Column(String, nullable=True)
    orders_filled = Column(Float, nullable=True)
    orders_remaining = Column(Float, nullable=True)
    fill_history = relationship('Fill')

    def __repr__(self):
        return f'{self.strategy_name} [{self.ORDER_STATE}] {self.init_id}'


class Fill(Base):
    __tablename__ = 'fill'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    timestamp = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)

    def __repr__(self):
        return f'{self.order_id} - {self.id} {self.timestamp} {self.quantity}'

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    s = session()

    sample_orders = [
        Order(ORDER_STATE='state', init_time='234234', strategy_name='st_1')
    ]

    sample_fills = [
        Fill(order_id=1, timestamp='23423', quantity=23.23),
        Fill(order_id=1, timestamp='23423', quantity=1)
    ]

    s.bulk_save_objects(sample_orders)
    s.bulk_save_objects(sample_fills)
    s.commit()

    orders = s.query(Order).all()

    print(orders[0])