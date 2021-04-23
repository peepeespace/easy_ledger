from django.db import models
from user.models import User

ORDER_STATE_CHOICES = [
    ('INIT', 'INIT'),
    ('OPEN', 'OPEN'),
    ('CLOSED', 'CLOSED'),
    ('FILLED', 'FILLED'),
]

SIDE_CHOICES = [
    ('B', 'BUY'),
    ('S', 'SELL'),
]

ORDER_TYPE_CHOICES = [
    ('L', 'LIMIT'),
    ('M', 'MARKET'),
]

POSITION_STATE_CHOICES = [
    ('OPEN', 'OPEN'),
    ('CLOSED', 'CLOSED'),
]


class ClientSession(models.Model):
    """
    Websocket 서버에서 필요한 유저 id, timestamp, refresh token, access token으로 만든 session_id 저장

    - 한 유저당 한개 connection 허용하기 위해서 user 정보 저장
    - 세션 시작을 기록하기 위해서 timestamp 저장
    - 소켓 서버에서 로그인이 되었는지 확인하기 위해서 is_authenticated 저장
    - 소켓 서버에서 요청 받은 유저 id, timestamp, refresh token, access token으로 hashing한 값이 session_id와 일치하면
      execution 기능을 활성화해주기 위해서 session_id를 저장
    - 소켓 통신에서 사용될 encryption method에 사용될 key 저장
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='sessions')
    is_authenticated = models.BooleanField(default=False, blank=True, null=True)
    timestamp = models.CharField(max_length=25, blank=True, null=True)
    session_type = models.CharField(max_length=50, blank=True, null=True) # ACTION, SUBSCRIPTION
    session_id = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f'[User ID: {self.user.id}] {self.session_id}'


class ExecutionSession(models.Model):
    """
    Client는 meta로 어떤 거래소/증권사를 execution engine으로 사용할지 설정한다.
    (예: 이베스트, 신한 등)
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='execution_sessions')
    meta = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    account_password = models.CharField(max_length=100, blank=True, null=True)
    public_key = models.CharField(max_length=150, blank=True, null=True)
    private_key = models.CharField(max_length=150, blank=True, null=True)
    execution_port = models.IntegerField(blank=True, null=True) # 주문을 넣는 포트
    account_port = models.IntegerField(blank=True, null=True)   # 결과값 (주문접수, 저문체결, 주문취소 등) 받는 포트
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[User ID: {self.user.id}] {self.meta} {self.execution_port} {self.account_port}'


class Ledger(models.Model):
    """
    여러 Ledger가 존재할 수 있다.

    Ledger에 여러 전략이 존재할 수 있는 형식이다.
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='ledgers')
    name = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[User ID: {self.user}] {self.name}'


class Strategy(models.Model):
    ledger = models.ForeignKey(Ledger,
                               on_delete=models.CASCADE,
                               related_name='strategies')
    name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[Ledger ID: {self.ledger}] {self.name}'


class Cash(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='cash')
    strategy_name = models.CharField(max_length=150, blank=True, null=True)
    quote = models.CharField(max_length=50, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[User ID: {self.user.id}] {self.strategy_name} {self.quote} {self.amount}'


class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='orders')
    strategy_name = models.CharField(max_length=150, blank=True, null=True)
    order_state = models.CharField(max_length=6, choices=ORDER_STATE_CHOICES, blank=True, null=True)
    init_time = models.CharField(max_length=25, blank=True, null=True)
    symbol = models.CharField(max_length=30, blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, blank=True, null=True)
    order_type = models.CharField(max_length=1, choices=ORDER_TYPE_CHOICES, blank=True, null=True)
    quote = models.CharField(max_length=100, blank=True, null=True)
    meta = models.CharField(max_length=100, blank=True, null=True)
    hash = models.CharField(max_length=100, blank=True, null=True)
    init_id = models.CharField(max_length=100, blank=True, null=True)
    open_id = models.CharField(max_length=100, blank=True, null=True)
    filled_id = models.CharField(max_length=100, blank=True, null=True)
    closed_id = models.CharField(max_length=100, blank=True, null=True)
    open_time = models.CharField(max_length=25, blank=True, null=True)
    closed_time = models.CharField(max_length=25, blank=True, null=True)
    order_number = models.CharField(max_length=25, blank=True, null=True)
    orders_filled = models.FloatField(blank=True, null=True)
    orders_remaining = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.strategy_name} {self.symbol} {self.price} {self.quote} {self.quantity} [{self.created}]'


class Fill(models.Model):
    """
    유저쪽에서 업데이트를 하는 경우 없음 (거래소 response를 기반으로 업데이트)
    """
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='fill_history')
    timestamp = models.CharField(max_length=25, blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.order} {self.timestamp} {self.quantity}'


class Position(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='positions')
    strategy_name = models.CharField(max_length=150, blank=True, null=True)
    position_state = models.CharField(max_length=6, choices=POSITION_STATE_CHOICES, blank=True, null=True)
    symbol = models.CharField(max_length=30, blank=True, null=True)
    quote = models.CharField(max_length=100, blank=True, null=True)
    meta = models.CharField(max_length=100, blank=True, null=True)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    average_price = models.FloatField(blank=True, null=True)
    invest_amount = models.FloatField(blank=True, null=True)
    borrow_amount = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'{self.strategy_name} {self.symbol} {self.side} {self.quantity}'


class Universe(models.Model):
    """
    관심 종목 (실제 트레이딩할 때 사용하게 될 유니버스 + 관심 종목으로 만들어진 유니버스)
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='universe')
    name = models.CharField(max_length=100, blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    code_list = models.TextField(blank=True, null=True) # 리스트가 separator로 나뉜 string 형식
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} {self.name} {self.date}'