# backend/apps/predictions/serializers.py

from rest_framework import serializers
from .models import ForecastModel, StockPrediction, PredictionMetrics

class ForecastModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastModel
        fields = '__all__'

class StockPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrediction
        fields = '__all__'

class PredictionMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionMetrics
        fields = '__all__'