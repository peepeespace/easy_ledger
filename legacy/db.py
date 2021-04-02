import sqlite3
import threading
import pandas as pd


class LedgerDB:

    def __init__(self):
        self.conn = sqlite3.connect('test.db')
        self.cur = self.conn.cursor()

        self._table_check()
        # self._auto_commit()

    # def _auto_commit(self):
    #     self.conn.commit()
    #     timer = threading.Timer(10, self._auto_commit)
    #     timer.setDaemon(True)
    #     timer.start()

    def _table_check(self):
        try:
            self.cur.execute("""
            CREATE TABLE order_hash_table (
                id integer primary key autoincrement,
                hash text not null,
                code text not null,
                quantity integer,
                price integer,
                side text,
                order_type text,
                strategies_with_current_order text);
            """)

            self.cur.execute("""
            CREATE TABLE open_orders (
                id integer primary key autoincrement,
                date text not null,
                order_number text not null,
                strategy_name text not null,
                register_time text not null,
                order_hash text not null,
                orders_filled integer,
                orders_remaining integer);
            """)

            self.cur.execute("""
            CREATE TABLE positions (
                id integer primary key autoincrement,
                strategy_name text not null,
                code text not null,
                side text not null,
                quantity integer,
                leverage integer);
            );
            """)
        except:
            pass

    # order hash table
    def get_order_hash_table_data(self, hash=None):
        if hash is None:
            sql = """
            SELECT * FROM order_hash_table;
            """
        else:
            sql = f"""
            SELECT * FROM order_hash_table WHERE hash='{hash}'
            """
        return pd.read_sql(sql, self.conn)

    def get_active_order_hash_table_data(self):
        sql = """
        SELECT * FROM order_hash_table WHERE strategies_with_current_order <> '';
        """
        return pd.read_sql(sql, self.conn)

    def add_strategy_to_current_order(self, hash, strategy):
        order = self.get_order_hash_table_data(hash=hash).iloc[0].to_dict()
        if order['strategies_with_current_order'] != '':
            strategies_with_current_order = order['strategies_with_current_order'].split(';')
            strategies_with_current_order.append(strategy)
        else:
            strategies_with_current_order = [strategy]

        strategies_with_current_order = ';'.join(strategies_with_current_order)

        sql = f"""
        UPDATE order_hash_table SET strategies_with_current_order='{strategies_with_current_order}'
        WHERE hash='{hash}';
        """
        self.cur.execute(sql)
        self.conn.commit()

    def save_order_hash_table_data(self, hash, code, quantity, price, side, order_type, strategies_with_current_order):
        sql = """
        INSERT INTO order_hash_table(hash, code, quantity, price, side, order_type, strategies_with_current_order)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        self.cur.execute(sql, (hash, code, quantity, price, side, order_type, strategies_with_current_order))
        self.conn.commit()

    # open orders
    def get_open_orders_data(self):
        sql = """
        SELECT * FROM open_orders;
        """
        return pd.read_sql(sql, self.conn)

    def get_active_open_orders_data(self):
        sql = """
        SELECT * FROM open_orders WHERE orders_remaining <> 0;
        """
        return pd.read_sql(sql, self.conn)

    def fill_open_orders_data(self):
        pass

    def save_open_orders_data(self, date, order_number, strategy_name, register_time, order_hash, orders_filled, orders_remaining):
        sql = """
        INSERT INTO open_orders(date, order_number, strategy_name, register_time, order_hash, orders_filled, orders_remaining)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        self.cur.execute(sql, (date, order_number, strategy_name, register_time, order_hash, orders_filled, orders_remaining))
        self.conn.commit()

    # positions
    def get_positions_data(self, strategy_name=None, code=None):
        pass

    def update_positions_data(self):
        pass

    def save_positions_data(self, strategy_name, code, side, quantity, leverage):
        sql = """
        INSERT INTO positions(strategy_name, code, side, quantity, leverage)
        VALUES (?, ?, ?, ?);
        """
        self.cur.execute(sql, (strategy_name, code, side, quantity, leverage))
        self.conn.commit()


if __name__ == '__main__':
    db = LedgerDB()

    d = db.get_active_order_hash_table_data()
    print(d)


    #
    # db.save_open_orders_data('20210101', 0, 'strat_1', '20210101090000', '123423sdf', 1, 10)
    # db.save_open_orders_data('20210101', 1, 'strat_2', '20210101090001', '234sdwfve', 10, 0)
    #
    # data = db.get_order_hash_table_data()
    # print(data)
    #
    # data = db.get_activate_open_orders_data()
    # print(data)