from django.urls import path
from db.views import (
    LedgerAPIView,
    StrategyAPIView,
    StrategyCreateAPIView,
)

urlpatterns = [
    path('ledger/', LedgerAPIView.as_view(), name='ledger'),
    path('strategy/', StrategyAPIView.as_view(), name='strategy'),
    path('strategy/create/', StrategyCreateAPIView.as_view(), name='create-strategy'),
]