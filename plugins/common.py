import zmq
import json
import uuid


class LedgerPlugin:

    def __init__(self, ledger_name, strategy_name):
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect('tcp://localhost:9999')

        self.session_id = str(uuid.uuid1())
        self.username = str(uuid.uuid1())
        self.ledger_name = ledger_name
        self.strategy_name = strategy_name
        self.req_common = {
            'session_id': self.session_id,
            'username': self.username,
            'ledger_name': self.ledger_name,
            'strategy_name': self.strategy_name
        }

        self._add_ledger()

    def _request(self, req):
        self.socket.send_string(json.dumps(req))
        res = self.socket.recv_string()
        return json.loads(res)

    def build_request_object(self, func_name, **params):
        return {
            'type': func_name,
            'params': {
                **self.req_common,
                **params
            }
        }

    def _add_ledger(self):
        req = self.build_request_object('add_ledger')
        return self._request(req)

    def get_cash(self, quote=None):
        req = self.build_request_object('get_cash', quote=quote)
        return self._request(req)

    def update_cash(self, amount, quote=None):
        req = self.build_request_object('update_cash', amount=amount, quote=quote)
        return self._request(req)

    def get_orders(self):
        pass

    def get_order(self, order_number):
        req = self.build_request_object('get_order', order_number=order_number)
        return self._request(req)

    def clean_orders(self, state):
        req = self.build_request_object('clean_orders', state=state)
        return self._request(req)

    def get_positions(self):
        req = self.build_request_object('get_positions')
        return self._request(req)

    def get_position(self, symbol):
        req = self.build_request_object('get_position', symbol=symbol)
        return self._request(req)

    def update_position(self, symbol, side, price, quantity, position_amount=None, order_state=None):
        req = self.build_request_object('update_position',
                                        symbol=symbol,
                                        side=side,
                                        price=price,
                                        quantity=quantity,
                                        position_amount=position_amount,
                                        order_state=order_state)
        return self._request(req)

if __name__ == '__main__':
    p = LedgerPlugin('ledger_1', 'strategy_1')
    cash = p.get_cash()
    print(cash)

    res = p.update_cash(10000, 'usdt')
    print(res)

    cash = p.get_cash('usdt')
    print(cash)

    position = p.get_position('005930')
    print(position)

    res = p.update_position(symbol='005930', side='SELL', price=900, quantity=1)
    print(res)
    res = p.update_position(symbol='005930', side='SELL', price=900, quantity=2)
    print(res)
    res = p.update_position(symbol='005930', side='SELL', price=900, quantity=3)
    print(res)

    position = p.get_position('005930')
    print(position)


    positions = p.get_positions()
    print(positions)