from django.db import models
from user.models import UserProfile

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


class Ledger(models.Model):
    """
    여러 Ledger가 존재할 수 있다.

    Ledger에 여러 전략이 존재할 수 있는 형식이다.
    """
    user = models.ForeignKey(UserProfile,
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


class Order(models.Model):
    user = models.ForeignKey(UserProfile,
                             on_delete=models.CASCADE,
                             related_name='orders')
    strategy_name = models.CharField(max_length=150)
    order_state = models.CharField(max_length=6, choices=ORDER_STATE_CHOICES, blank=True, null=True)
    init_time = models.CharField(max_length=25, blank=True, null=True)
    symbol = models.CharField(max_length=30, blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, blank=True, null=True)
    order_type = models.CharField(max_length=1, choices=ORDER_TYPE_CHOICES, blank=True, null=True)
    meta = models.CharField(max_length=100, blank=True, null=True)
    hash = models.CharField(max_length=100, blank=True, null=True)
    init_id = models.CharField(max_length=100, blank=True, null=True)
    open_id = models.CharField(max_length=100, blank=True, null=True)
    filled_id = models.CharField(max_length=100, blank=True, null=True)
    open_time = models.CharField(max_length=25, blank=True, null=True)
    order_number = models.CharField(max_length=25, blank=True, null=True)
    orders_filled = models.FloatField(blank=True, null=True)
    orders_remaining = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.strategy.name} {self.symbol} {self.price} {self.quantity} [{self.created}]'


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
    user = models.ForeignKey(UserProfile,
                             on_delete=models.CASCADE,
                             related_name='positions')
    strategy_name = models.CharField(max_length=150)
    position_state = models.CharField(max_length=6, choices=POSITION_STATE_CHOICES, blank=True, null=True)
    symbol = models.CharField(max_length=30, blank=True, null=True)
    meta = models.CharField(max_length=100, blank=True, null=True)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    average_price = models.FloatField(blank=True, null=True)
    invest_amount = models.FloatField(blank=True, null=True)
    borrow_amount = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'{self.strategy.name} {self.symbol} {self.side} {self.quantity}'


class Universe(models.Model):
    """
    관심 종목 (실제 트레이딩할 때 사용하게 될 유니버스 + 관심 종목으로 만들어진 유니버스)
    """
    user = models.ForeignKey(UserProfile,
                             on_delete=models.CASCADE,
                             related_name='universe')
    name = models.CharField(max_length=100, blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    code_list = models.TextField(blank=True, null=True) # 리스트가 separator로 나뉜 string 형식
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} {self.name} {self.date}'