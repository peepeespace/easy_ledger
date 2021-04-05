import zmq
import json
import traceback

from ledger import Ledger


class LedgerServer:

    def __init__(self):
        self.ledger = Ledger()

        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REP)
        self.socket.bind("tcp://*:5500")

    def order_hash(self, symbol, price, quantity, side, order_type, meta=None, **kwargs):
        order_hash = self.ledger.order_hash(symbol=symbol, price=price, quantity=quantity, side=side,
                                            order_type=order_type, meta=meta)
        return {'status': 'SUCCESS', 'result': order_hash}

    def get_order(self, strategy_name, order_number, **kwargs):
        order = self.ledger.get_order(strategy_name=strategy_name, order_number=order_number)
        return {'status': 'SUCCESS', 'result': order}

    def get_position(self, strategy_name, symbol, **kwargs):
        position = self.ledger.get_position(strategy_name=strategy_name, symbol=symbol)
        return {'status': 'SUCCESS', 'result': position}

    def init_order(self, strategy_name, symbol, price, quantity, side, order_type, meta=None, **kwargs):
        order_hash = self.ledger.init_order(strategy_name=strategy_name, symbol=symbol, price=price, quantity=quantity,
                                            side=side, order_type=order_type, meta=meta)
        return {'status': 'SUCCESS', 'result': order_hash}

    def register_order(self, order_number, order_hash, **kwargs):
        strategy_name = self.ledger.register_order(order_number=order_number, order_hash=order_hash)
        return {'status': 'SUCCESS', 'result': self.ledger.get_order(strategy_name, order_number)}

    def fill_order(self, strategy_name, order_number, price, quantity, position_amount=None, **kwargs):
        self.ledger.fill_order(strategy_name=strategy_name, order_number=order_number, price=price,
                               quantity=quantity, position_amount=position_amount)
        return {'status': 'SUCCESS', 'result': self.ledger.get_order(strategy_name, order_number)}

    def start(self):
        while True:
            req = self.socket.recv_string()
            print("Received request: %s" % req)

            try:
                req = json.loads(req)
                request_type = req.get('type')
                params = req.get('params', {})

                if request_type == 'order_hash':
                    res = self.order_hash(**params)

                if request_type == 'get_order':
                    res = self.get_order(**params)

                if request_type == 'get_position':
                    res = self.get_position(**params)

                if request_type == 'init_order':
                    res = self.init_order(**params)

                if request_type == 'register_order':
                    res = self.register_order(**params)

                if request_type == 'fill_order':
                    res = self.fill_order(**params)

            except:
                res = {'status': 'ERROR', 'message': traceback.format_exc()}

            self.socket.send_string(json.dumps(res))


if __name__ == '__main__':
    server = LedgerServer()
    server.start()