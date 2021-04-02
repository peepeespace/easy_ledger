import os
import pickle


class OrderQueue:
    """
    원장 클라이언트에서 주문이 발생하면 hash를 계산하여 바로 주문을 추가하여야 한다.

    거래소에서 주문 접수가 완료되면 큐에서 제거한다.
    현재 클라이언트측에서 발생한 주문에 대한 정보를 기록하기 위해서 필요한 자료 구조이다.

    자료 구조는 피클로 모든 트랜잭션이 발생할 때마다 새로운 상태를 저장하여 프로그램이 종류된 후 다시
    실행하더라도 데이터 손실이 없도록 한다.
    """

    CACHE_NAME = 'OrderQueue.pkl'

    def __init__(self):
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.CACHE_NAME):
            f = open(self.CACHE_NAME, 'rb')
            self.q = pickle.load(f)
        else:
            self.q = []
            self._save_state()

    def _save_state(self):
        with open(self.CACHE_NAME, 'wb') as f:
            pickle.dump(self.q, f)

    @property
    def order_count(self):
        return len(self.q)

    def add_order(self, order_hash):
        self.q.append(order_hash)
        self._save_state()
        return order_hash

    def remove_order(self, order_hash):
        self.q.remove(order_hash)
        self._save_state()
        return order_hash


if __name__ == '__main__':
    q = OrderQueue()
    print(q.order_count)

    order_hash = q.add_order('hash')
    print(q.order_count)

    print(q.q)

    q.remove_order(order_hash)
    print(q.q)