# backend/apps/predictions/views_prophet.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import logging

from .services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

class ProphetPredictionViewSet(viewsets.ViewSet):
    """
    API endpoint for Prophet model predictions
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prediction_service = PredictionService()
    
    @action(detail=False, methods=['get'])
    def predict(self, request):
        """
        Hisse senedi için Prophet tabanlı fiyat tahmini yapar
        """
        symbol = request.query_params.get('symbol')
        forecast_days = request.query_params.get('forecast_days', 30)
        include_news = request.query_params.get('include_news', 'true').lower() == 'true'
        
        if not symbol:
            return Response(
                {'error': 'Stock symbol is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            forecast_days = int(forecast_days)
        except (TypeError, ValueError):
            forecast_days = 30
        
        result = self.prediction_service.predict_with_prophet(
            symbol, forecast_days, include_news)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def news_impact(self, request):
        """
        Haberlerin hisse senedi fiyatı üzerindeki etkisini analiz eder
        """
        symbol = request.query_params.get('symbol')
        days_back = request.query_params.get('days_back', 30)
        
        if not symbol:
            return Response(
                {'error': 'Stock symbol is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            days_back = int(days_back)
        except (TypeError, ValueError):
            days_back = 30
        
        result = self.prediction_service.analyze_news_impact(symbol, days_back)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def sentiment_scenarios(self, request):
        """
        Farklı haber duyarlılığı senaryolarına göre tahminler oluşturur
        """
        symbol = request.query_params.get('symbol')
        forecast_days = request.query_params.get('forecast_days', 30)
        
        if not symbol:
            return Response(
                {'error': 'Stock symbol is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            forecast_days = int(forecast_days)
        except (TypeError, ValueError):
            forecast_days = 30
        
        result = self.prediction_service.create_sentiment_scenarios(
            symbol, forecast_days)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def analyze_stock_with_news(self, request):
        """
        Belirli bir hisse senedi için kapsamlı haber ve fiyat analizi yapar
        """
        symbol = request.query_params.get('symbol')
        days_back = request.query_params.get('days_back', 60)
        forecast_days = request.query_params.get('forecast_days', 30)
        
        if not symbol:
            return Response(
                {'error': 'Stock symbol is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            days_back = int(days_back)
            forecast_days = int(forecast_days)
        except (TypeError, ValueError):
            days_back = 60
            forecast_days = 30
        
        # Haber etkisi analizi
        news_impact = self.prediction_service.analyze_news_impact(symbol, days_back)
        
        # Prophet tahminleri
        prediction = self.prediction_service.predict_with_prophet(
            symbol, forecast_days, include_news=True)
        
        # Duyarlılık senaryoları
        scenarios = self.prediction_service.create_sentiment_scenarios(
            symbol, forecast_days)
        
        # Sonuçları birleştir
        result = {
            'symbol': symbol,
            'days_analyzed': days_back,
            'forecast_days': forecast_days,
            'news_impact_analysis': news_impact,
            'price_forecast': prediction,
            'sentiment_scenarios': scenarios,
            'timestamp': prediction.get('timestamp', '')
        }
        
        return Response(result)