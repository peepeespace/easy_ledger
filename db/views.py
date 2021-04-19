from db.models import (
    Ledger,
    Strategy,
    Order,
    Fill,
    Position,
    Universe,
)
from db.serializers import (
    LedgerSerializer,
    StrategySerializer,
    OrderSerializer,
    FillSerializer,
    PositionSerializer,
    UniverseSerializer,
)

from db.permissions import IsOwner
from rest_framework import pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter, OrderingFilter


class StandardResultPagination(pagination.PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    # max_page_size = 1000


class LedgerAPIView(generics.ListCreateAPIView):
    queryset = Ledger.objects.all()
    serializer_class = LedgerSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandardResultPagination
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self, *args, **kwargs):
        queryset = Ledger.objects.all().order_by('id')
        return queryset


class StrategyAPIView(generics.ListAPIView):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandardResultPagination
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self, *args, **kwargs):
        queryset = Strategy.objects.all().order_by('id')
        return queryset


class StrategyCreateAPIView(APIView):
    def post(self, request):
        ledger_id = request.data.get('ledger_id')
        ledger = Ledger.objects.filter(id=ledger_id).first()

        if request.user != ledger.user:
            return Response({'fail': 'cannot access ledger. no permission'}, status=400)

        name = request.data.get('name')
        account_number = request.data.get('account_number')
        description = request.data.get('description')

        st = Strategy(
            ledger=ledger_id,
            name=name,
            account_number=account_number,
            description=description
        )
        st.save()

        return Response({'success': 'created strategy'}, status=201)


# class OrdersAPIView(generics.ListAPIView):
#     queryset = Orders.objects.all()
#     serializer_class = OrdersSerializer
#     permission_classes = (permissions.AllowAny,)
#     pagination_class = StandardResultPagination
#     filter_backends = [SearchFilter, OrderingFilter]
#
#     def get_queryset(self, *args, **kwargs):
#         queryset = Orders.objects.all().order_by('id')
#         strategy_by = self.request.GET.get('strategy')
#         date_by = self.request.GET.get('date')
#         start = self.request.GET.get('start')
#         end = self.request.GET.get('end')
#         code_by = self.request.GET.get('code')
#         if strategy_by:
#             queryset = queryset.filter(strategy=strategy_by)
#         if date_by:
#             queryset = queryset.filter(date=date_by)
#         if start and end and not date_by:
#             queryset = queryset.filter(date__gte=start).filter(date__lte=end)
#         if code_by:
#             queryset = queryset.filter(code=code_by)
#         return queryset
#
#
# class HoldingsAPIView(generics.ListAPIView):
#     queryset = Holdings.objects.all()
#     serializer_class = HoldingsSerializer
#     permission_classes = (permissions.AllowAny,)
#     pagination_class = StandardResultPagination
#     filter_backends = [SearchFilter, OrderingFilter]
#
#     def get_queryset(self, *args, **kwargs):
#         queryset = Holdings.objects.all().order_by('id')
#         strategy_by = self.request.GET.get('strategy')
#         date_by = self.request.GET.get('date')
#         start = self.request.GET.get('start')
#         end = self.request.GET.get('end')
#         code_by = self.request.GET.get('code')
#         if strategy_by:
#             queryset = queryset.filter(strategy=strategy_by)
#         if date_by:
#             queryset = queryset.filter(date=date_by)
#         if start and end and not date_by:
#             queryset = queryset.filter(date__gte=start).filter(date__lte=end)
#         if code_by:
#             queryset = queryset.filter(code=code_by)
#         return queryset
#
#
# class MonitorListAPIView(generics.ListAPIView):
#     queryset = MonitorList.objects.all()
#     serializer_class = MonitorListSerializer
#     permission_classes = (permissions.AllowAny,)
#     pagination_class = StandardResultPagination
#     filter_backends = [SearchFilter, OrderingFilter]
#
#     def get_queryset(self, *args, **kwargs):
#         queryset = MonitorList.objects.all().order_by('id')
#         strategy_by = self.request.GET.get('strategy')
#         date_by = self.request.GET.get('date')
#         start = self.request.GET.get('start')
#         end = self.request.GET.get('end')
#         if strategy_by:
#             queryset = queryset.filter(strategy=strategy_by)
#         if date_by:
#             queryset = queryset.filter(date=date_by)
#         if start and end and not date_by:
#             queryset = queryset.filter(date__gte=start).filter(date__lte=end)
#         return queryset