from django.urls import path
from db.views import (
    LedgerAPIView,
    StrategyAPIView,
)

urlpatterns = [
    path('ledger/', LedgerAPIView.as_view(), name='ledger'),
    path('strategy/', StrategyAPIView.as_view(), name='strategy'),
]