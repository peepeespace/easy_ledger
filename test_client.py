import zmq
import json
from multiprocessing import Process


def send_req():
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5500")

    req = {
        'type': 'get_position',
        'params': {
            'strategy_name': 'strategy_2',
            'symbol': '005930'
        }
    }
    socket.send_string(json.dumps(req))
    message = socket.recv_string()
    print(json.loads(message))

    # req = {
    #     'type': 'init_order',
    #     'params': {
    #         'strategy_name': 'strategy_2',
    #         'symbol': '005930',
    #         'price': 40000,
    #         'quantity': 20,
    #         'side': 'BUY',
    #         'order_type': 'MARKET',
    #         'meta': 'stock.ebest'
    #     }
    # }
    # socket.send_string(json.dumps(req))
    # message = socket.recv_string()
    # print(json.loads(message))
    #
    # order_hash = json.loads(message)['result']
    # order_number = 'ordernumber123123'
    #
    # req = {
    #     'type': 'register_order',
    #     'params': {
    #         'order_number': order_number,
    #         'order_hash': order_hash
    #     }
    # }
    # socket.send_string(json.dumps(req))
    # message = socket.recv_string()
    # print(json.loads(message))
    #
    # req = {
    #     'type': 'fill_order',
    #     'params': {
    #         'strategy_name': 'strategy_2',
    #         'order_number': 'ordernumber123123',
    #         'price': 39000,
    #         'quantity': 10,
    #         'position_amount': 39000 * -10
    #     }
    # }
    # socket.send_string(json.dumps(req))
    # message = socket.recv_string()
    # print(json.loads(message))
    #
    # req = {
    #     'type': 'get_order',
    #     'params': {
    #         'strategy_name': 'strategy_2',
    #         'order_number': 'ordernumber123123'
    #     }
    # }
    # socket.send_string(json.dumps(req))
    # message = socket.recv_string()
    # print(json.loads(message))

if __name__ == '__main__':
    p = Process(target=send_req)
    p.start()