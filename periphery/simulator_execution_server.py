import zmq
import json
import pika
import traceback


class SimulatorExecutionServer:
    """
    Simulation으로 주문을 전송하고 응답을 받기 위해서 필요한 서버
    """

    def __init__(self):
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REP)
        self.socket.bind('tcp://*:9998')

        credentials = pika.PlainCredentials('qraft', 'developer')
        parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
        self.rabbit_queue = pika.BlockingConnection(parameters)
        self.channel = self.rabbit_queue.channel()
        self.channel.exchange_declare('ledger_exchange', exchange_type='topic')

    def _send(self, res):
        self.socket.send_string(json.dumps(res))

    def start_server(self):
        print('Starting simulator execution server')
        while True:
            req = self.socket.recv_string()
            req = json.loads(req)
            print(req)

            try:
                req_type = req['type']

                if req_type == 'send_order':
                    self.send_order(request=req)

                elif req_type == 'cancel_order':
                    pass

                elif req_type == 'replace_order':
                    pass

                else:
                    pass

                self._send({'status': 'success'})
            except:
                traceback.print_exc()
                self._send({'status': 'failed'})

    def send_order(self, request):
        session_id = request['session_id']
        res = {
            'session_id': session_id,
            '단축코드': '005930',
            '주문수량': 10,
            '주문가격': 100
        }
        self.channel.basic_publish(exchange='ledger_exchange',
                                   routing_key=session_id,
                                   body=json.dumps(res))
        print(f'Sent: {json.dumps(res)}')

    def cancel_order(self, request):
        pass

    def replace_order(self, request):
        pass