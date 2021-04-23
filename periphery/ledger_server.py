import zmq
import json
import uuid
import traceback

from core.ledger import Ledger


class LedgerServer:
    """
    SocketServer와 소통하게 될 Ledger 매니저 서버

    웹소켓 서버로부터 세션 등록을 요청하면 그 유저의 Ledger를 생성한다.
    """

    def __init__(self):
        self.ledgers = {}

        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REP)
        self.socket.bind('tcp://*:9999')

    def _send(self, res):
        self.socket.send_string(json.dumps(res))

    def start_server(self):
        print('Starting ledger server')
        while True:
            req = self.socket.recv_string()
            req = json.loads(req)
            print(req)

            try:
                req_type = req['type']

                if req_type == 'ping':
                    self._send({'status': 'success', 'result': 'pong'})

                elif req_type == 'add_ledger':
                    params = req.get('params', {})
                    ledger_name = self.add_ledger(**params)
                    self._send({'status': 'success', 'result': ledger_name})

                elif req_type == 'get_cash':
                    params = req.get('params', {})
                    cash = self.get_cash(**params)
                    self._send({'status': 'success', 'result': cash})

                elif req_type == 'update_cash':
                    params = req.get('params', {})
                    self.update_cash(**params)
                    self._send({'status': 'success', 'result': f'{req_type} successful'})

                elif req_type == 'get_orders':
                    params = req.get('params', {})
                    self.get_orders(**params)
                    self._send({'status': 'success', 'result': f'{req_type} successful'})

                elif req_type == 'get_order':
                    params = req.get('params', {})
                    order = self.get_order(**params)
                    self._send({'status': 'success', 'result': order})

                elif req_type == 'clean_orders':
                    params = req.get('params', {})
                    self.clean_orders(**params)
                    self._send({'status': 'success', 'result': f'{req_type} successful'})

                elif req_type == 'get_positions':
                    params = req.get('params', {})
                    self.get_positions(**params)
                    self._send({'status': 'success', 'result': f'{req_type} successful'})

                elif req_type == 'get_position':
                    params = req.get('params', {})
                    order = self.get_position(**params)
                    self._send({'status': 'success', 'result': order})

                elif req_type == 'update_position':
                    params = req.get('params', {})
                    self.update_position(**params)
                    self._send({'status': 'success', 'result': f'{req_type} successful'})

                else:
                    self._send({'status': 'failed', 'result': 'no type field'})

            except:
                traceback.print_exc()
                self._send({'status': 'error', 'result': 'wrong request format. type field is required.'})

    def add_ledger(self, session_id, username=None, ledger_name=None, **kwargs):
        if ledger_name is None:
            ledger_name = str(uuid.uuid1())

        if session_id not in self.ledgers:
            self.ledgers[session_id] = {}

        if ledger_name not in self.ledgers[session_id]:
            self.ledgers[session_id][ledger_name] = Ledger(name=ledger_name,
                                                           username=username,
                                                           auto_save=True,
                                                           db_save=False)
        return ledger_name

    def get_ledger(self, session_id, username, ledger_name, **kwargs):
        self.add_ledger(session_id, username, ledger_name)
        return self.ledgers[session_id][ledger_name]

    def get_cash(self, session_id, username, ledger_name, strategy_name, quote=None, **kwargs):
        ledger = self.get_ledger(session_id, username, ledger_name)
        return ledger.get_cash(strategy_name=strategy_name, quote=quote)

    def update_cash(self, session_id, username, ledger_name, strategy_name, amount, quote=None, **kwargs):
        ledger = self.get_ledger(session_id, username, ledger_name)
        ledger.update_cash(strategy_name=strategy_name, amount=amount, quote=quote)

    def get_orders(self, session_id, username, ledger_name, strategy_name, **kwargs):
        ledger = self.get_ledger(session_id, username, ledger_name)
        orders = ledger.get_orders(strategy_name=strategy_name)
        print(orders)

    def get_order(self, session_id, username, ledger_name, strategy_name, order_number, **kwargs):
        ledger = self.get_ledger(session_id, username, ledger_name)
        order = ledger.get_order(strategy_name=strategy_name,
                                 order_number=order_number,
                                 format='dict')
        return order

    def clean_orders(self, session_id, username, ledger_name, strategy_name, state):
        ledger = self.get_ledger(session_id, username, ledger_name)
        ledger.clean_orders(state=state,
                            strategy_name=strategy_name)

    def get_positions(self, session_id, username, ledger_name, strategy_name):
        ledger = self.get_ledger(session_id, username, ledger_name)
        positions = ledger.get_positions(strategy_name=strategy_name)
        print(positions)

    def get_position(self, session_id, username, ledger_name, strategy_name, symbol):
        ledger = self.get_ledger(session_id, username, ledger_name)
        position = ledger.get_position(strategy_name=strategy_name,
                                       symbol=symbol,
                                       format='dict')
        return position

    def update_position(self, session_id, username, ledger_name, strategy_name, symbol,
                        side, price, quantity, position_amount=None, order_state=None):
        ledger = self.get_ledger(session_id, username, ledger_name)
        ledger.update_position(strategy_name=strategy_name,
                               symbol=symbol,
                               side=side,
                               price=price,
                               quantity=quantity,
                               position_amount=position_amount,
                               order_state=order_state)

if __name__ == '__main__':
    ls = LedgerServer()
    ls.start_server()