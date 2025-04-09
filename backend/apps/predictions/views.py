# backend/apps/predictions/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import pandas as pd
import numpy as np
import json
import logging

from .models import ForecastModel, StockPrediction, PredictionMetrics
from .serializers import (
    ForecastModelSerializer, StockPredictionSerializer, 
    PredictionMetricsSerializer
)
from .ml_models.traditional_models import MarketDirectionPredictor
from .ml_models.deep_learning import LSTMNewsModel, BERTNewsModel
from .ml_models.hybrid_models import HybridMarketNewsModel
from .ml_models.model_evaluation import ModelEvaluator
from .data_processors.news_processor import NewsProcessor

logger = logging.getLogger(__name__)

class ForecastModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for forecast models
    """
    queryset = ForecastModel.objects.all()
    serializer_class = ForecastModelSerializer

class StockPredictionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for stock predictions
    """
    queryset = StockPrediction.objects.all()
    serializer_class = StockPredictionSerializer
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get latest predictions for a stock
        """
        stock_symbol = request.query_params.get('symbol')
        days = request.query_params.get('days', 7)
        
        try:
            days = int(days)
        except (TypeError, ValueError):
            days = 7
            
        if not stock_symbol:
            return Response(
                {'error': 'Stock symbol is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get the latest predictions for the stock
        predictions = StockPrediction.objects.filter(
            stock__symbol=stock_symbol
        ).order_by('-prediction_date')[:days]
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate a new prediction for a stock
        """
        stock_symbol = request.data.get('symbol')
        days = request.data.get('days', 1)
        
        if not stock_symbol:
            return Response(
                {'error': 'Stock symbol is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # In a real application, you would call your prediction model here
        # For demonstration, we'll return mock data
        
        return Response({
            'message': f'Prediction generated for {stock_symbol} for {days} days',
            'status': 'success'
        })

class PredictionMetricsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for prediction metrics
    """
    queryset = PredictionMetrics.objects.all()
    serializer_class = PredictionMetricsSerializer

class ModelComparisonViewSet(viewsets.ViewSet):
    """
    API endpoint for ML model comparison
    """
    
    @action(detail=False, methods=['get'])
    def compare(self, request):
        """
        Compare performance of all models
        """
        # In a real application, you would load saved metrics from the database
        # or recompute them based on test data
        # For demonstration, we'll return mock data
        
        comparison_results = {
            'LogisticRegression': {
                'accuracy': 0.76,
                'precision': 0.72,
                'recall': 0.68,
                'f1': 0.70,
                'roc_auc': 0.82,
                'execution_time': 0.15
            },
            'RandomForest': {
                'accuracy': 0.82,
                'precision': 0.79,
                'recall': 0.73,
                'f1': 0.76,
                'roc_auc': 0.88,
                'execution_time': 0.32
            },
            'LSTM': {
                'accuracy': 0.80,
                'precision': 0.76,
                'recall': 0.83,
                'f1': 0.79,
                'roc_auc': 0.86,
                'execution_time': 1.45
            },
            'BERT': {
                'accuracy': 0.85,
                'precision': 0.84,
                'recall': 0.81,
                'f1': 0.82,
                'roc_auc': 0.90,
                'execution_time': 2.78
            },
            'BERT-LSTM': {
                'accuracy': 0.88,
                'precision': 0.87,
                'recall': 0.86,
                'f1': 0.86,
                'roc_auc': 0.92,
                'execution_time': 3.25
            }
        }
        
        return Response(comparison_results)
    
    @action(detail=False, methods=['post'])
    def test_models(self, request):
        """
        Test all models on provided data and return comparison
        """
        texts = request.data.get('texts', [])
        labels = request.data.get('labels', [])
        
        if not texts or not labels or len(texts) != len(labels):
            return Response(
                {'error': 'Valid texts and labels arrays of equal length are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Process texts
        news_processor = NewsProcessor()
        processed_texts = [news_processor.preprocess_text(text) for text in texts]
        
        # Create models
        models = {
            'LogisticRegression': MarketDirectionPredictor(model_type='logistic_regression'),
            'RandomForest': MarketDirectionPredictor(model_type='random_forest')
        }
        
        # Split data (in a real app, you would have proper test/train split)
        # Here we just use the same data for demonstration
        X_train = processed_texts
        y_train = labels
        X_test = processed_texts
        y_test = labels
        
        # Train and evaluate models
        results = {}
        for name, model in models.items():
            model.train(X_train, y_train)
            metrics = model.evaluate(X_test, y_test)
            results[name] = metrics
        
        return Response(results)

class SentimentAnalysisViewSet(viewsets.ViewSet):
    """
    API endpoint for sentiment analysis
    """
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Analyze sentiment of provided texts
        """
        texts = request.data.get('texts', [])
        
        if not texts:
            return Response(
                {'error': 'No texts provided for analysis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Process texts for sentiment analysis
        news_processor = NewsProcessor()
        
        results = []
        for text in texts:
            processed_text = news_processor.preprocess_text(text)
            features = news_processor.extract_features(processed_text)
            
            # Calculate mock sentiment score (in a real app, use an actual ML model)
            sentiment_score = (features['positive_count'] - features['negative_count']) / \
                              (features['positive_count'] + features['negative_count'] + 1)
                              
            sentiment_label = 'positive' if sentiment_score > 0.2 else \
                             'negative' if sentiment_score < -0.2 else 'neutral'
                             
            results.append({
                'text': text,
                'processed_text': processed_text,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'features': features
            })
            
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def over_time(self, request):
        """
        Get sentiment analysis over time for a given period
        """
        time_range = request.query_params.get('time_range', '7d')
        
        # Generate mock data for sentiment over time
        sentiment_over_time = [
            {'date': '2025-03-01', 'positive': 45, 'neutral': 30, 'negative': 25},
            {'date': '2025-03-02', 'positive': 42, 'neutral': 33, 'negative': 25},
            {'date': '2025-03-03', 'positive': 38, 'neutral': 32, 'negative': 30},
            {'date': '2025-03-04', 'positive': 35, 'neutral': 30, 'negative': 35},
            {'date': '2025-03-05', 'positive': 30, 'neutral': 35, 'negative': 35},
            {'date': '2025-03-06', 'positive': 32, 'neutral': 33, 'negative': 35},
            {'date': '2025-03-07', 'positive': 38, 'neutral': 32, 'negative': 30},
        ]
        
        # Example sentiment distribution
        sentiment_counts = {
            'positive': 260,
            'neutral': 225,
            'negative': 215
        }
        
        # Example top positive and negative headlines
        top_positive = [
            {'headline': 'Market rallies as tech stocks surge', 'score': 0.92},
            {'headline': 'Economic growth exceeds expectations in Q1', 'score': 0.89},
            {'headline': 'Inflation data shows signs of cooling', 'score': 0.85},
            {'headline': 'Company XYZ reports record profits', 'score': 0.84},
            {'headline': 'Fed signals potential rate cuts later this year', 'score': 0.82}
        ]
        
        top_negative = [
            {'headline': 'Global markets tumble amid recession fears', 'score': -0.95},
            {'headline': 'Company ABC misses earnings expectations', 'score': -0.88},
            {'headline': 'Oil prices plummet as demand weakens', 'score': -0.85},
            {'headline': 'Tech layoffs continue as growth slows', 'score': -0.83},
            {'headline': 'Rising interest rates pressure housing market', 'score': -0.81}
        ]
        
        response_data = {
            'sentiment_over_time': sentiment_over_time,
            'sentiment_counts': sentiment_counts,
            'top_positive': top_positive,
            'top_negative': top_negative,
            'total_articles': sum(sentiment_counts.values()),
            'overall_sentiment': 'Neutral'  # or Positive/Negative
        }
        
        return Response(response_data)

class MarketPredictionViewSet(viewsets.ViewSet):
    """
    API endpoint for market predictions
    """
    
    @action(detail=False, methods=['post'])
    def predict_direction(self, request):
        """
        Predict market direction based on news headlines
        """
        texts = request.data.get('texts', [])
        model_type = request.data.get('model_type', 'bert-lstm')  # logistic_regression, random_forest, lstm, bert, bert-lstm
        
        if not texts:
            return Response(
                {'error': 'No texts provided for prediction'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # In a real application, we would load and use the appropriate model
        # For demonstration, we'll generate mock predictions
        
        import random
        
        predictions = []
        for text in texts:
            # Simulate different model confidence levels
            if model_type == 'bert-lstm':
                confidence = random.uniform(0.65, 0.95)
            elif model_type in ['bert', 'lstm']:
                confidence = random.uniform(0.60, 0.90)
            else:
                confidence = random.uniform(0.55, 0.85)
                
            direction = 'up' if confidence > 0.5 else 'down'
            
            predictions.append({
                'text': text,
                'predicted_direction': direction,
                'confidence': confidence
            })
        
        return Response({
            'predictions': predictions,
            'model_type': model_type
        })