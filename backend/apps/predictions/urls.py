# backend/apps/predictions/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_prophet

router = DefaultRouter()
router.register(r'models', views.ForecastModelViewSet, basename='forecast-model')
router.register(r'predictions', views.StockPredictionViewSet, basename='stock-prediction')
router.register(r'metrics', views.PredictionMetricsViewSet, basename='prediction-metrics')
router.register(r'model-comparison', views.ModelComparisonViewSet, basename='model-comparison')
router.register(r'sentiment-analysis', views.SentimentAnalysisViewSet, basename='sentiment-analysis')
router.register(r'market-prediction', views.MarketPredictionViewSet, basename='market-prediction')
router.register(r'prophet', views_prophet.ProphetPredictionViewSet, basename='prophet-prediction')

urlpatterns = [
    path('', include(router.urls)),
    path('compare-models/', views.ModelComparisonViewSet.as_view({'get': 'compare'}), name='compare-models'),
    path('sentiment-over-time/', views.SentimentAnalysisViewSet.as_view({'get': 'over_time'}), name='sentiment-over-time'),
    path('analyze-sentiment/', views.SentimentAnalysisViewSet.as_view({'post': 'analyze'}), name='analyze-sentiment'),
    path('predict-market-direction/', views.MarketPredictionViewSet.as_view({'post': 'predict_direction'}), name='predict-market-direction'),
    
    # Prophet bazlı tahmini API endpoint'leri
    path('prophet-predict/', views_prophet.ProphetPredictionViewSet.as_view({'get': 'predict'}), name='prophet-predict'),
    path('news-impact/', views_prophet.ProphetPredictionViewSet.as_view({'get': 'news_impact'}), name='news-impact'),
    path('sentiment-scenarios/', views_prophet.ProphetPredictionViewSet.as_view({'get': 'sentiment_scenarios'}), name='sentiment-scenarios'),
    path('analyze-stock-with-news/', views_prophet.ProphetPredictionViewSet.as_view({'get': 'analyze_stock_with_news'}), name='analyze-stock-with-news'),
]