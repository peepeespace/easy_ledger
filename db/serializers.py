from rest_framework import serializers
from db.models import (
    Ledger,
    Strategy,
    Order,
    Fill,
    Position,
    Universe,
)


class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = '__all__'


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class FillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fill
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class UniverseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universe
        fields = '__all__'