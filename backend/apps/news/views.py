# backend/apps/news/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from datetime import datetime, timedelta

from apps.accounts.models import UserPreference
from apps.stocks.models import Stock
from .services.news_service import NewsService
from .sentiment.analyzers import NewsSentimentAnalyzer, CombinedSentimentAnalyzer
from .sentiment.visualizers import SentimentDistributionVisualizer, SentimentTimeSeriesVisualizer

import logging

logger = logging.getLogger(__name__)

# Haber servisi instance'ı oluştur
news_service = NewsService()
sentiment_analyzer = NewsSentimentAnalyzer()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_list(request):
    """
    Genel finansal haberleri listeler
    """
    try:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        news_data = news_service.get_general_financial_news(page=page, page_size=page_size)
        
        # Error kontrolü
        if 'error' in news_data:
            # Get status code from service response or default to 500
            status_code = news_data.get('status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Log the specific error
            error_message = news_data.get('error', 'Unknown error')
            logger.error(f"News service error: {error_message} (Status: {status_code})")
            
            # Remove status_code from response to client
            if 'status_code' in news_data:
                del news_data['status_code']
                
            return Response(news_data, status=status_code)
        
        return Response(news_data)
        
    except Exception as e:
        logger.error(f"Error in news_list view: {str(e)}")
        return Response(
            {"error": "Failed to fetch news", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_detail(request, news_id):
    """
    Belirli bir haberin detaylarını gösterir
    """
    try:
        # Gerçek uygulamada haber ID'sine göre detay alınacak, örnek response:
        news = {
            'id': news_id,
            'title': 'Sample News Title',
            'description': 'This is a sample news description.',
            'content': 'This is the full content of the news article...',
            'source': 'Financial Times',
            'url': 'https://www.ft.com/sample-news',
            'published_at': datetime.now().isoformat(),
            'author': 'John Doe',
            'image_url': 'https://example.com/image.jpg',
            'related_symbols': ['AAPL', 'MSFT'],
            'sentiment': {
                'score': 0.65,
                'label': 'positive'
            }
        }
        
        return Response(news)
        
    except Exception as e:
        logger.error(f"Error in news_detail view for news ID {news_id}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch news details for ID {news_id}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_categories(request):
    """
    Haber kategorilerini listeler
    """
    try:
        # Örnek kategori listesi
        categories = [
            {'id': 'business', 'name': 'Business'},
            {'id': 'technology', 'name': 'Technology'},
            {'id': 'markets', 'name': 'Markets'},
            {'id': 'economy', 'name': 'Economy'},
            {'id': 'finance', 'name': 'Finance'},
            {'id': 'crypto', 'name': 'Cryptocurrency'},
            {'id': 'startups', 'name': 'Startups'},
            {'id': 'investing', 'name': 'Investing'}
        ]
        
        return Response(categories)
        
    except Exception as e:
        logger.error(f"Error in news_categories view: {str(e)}")
        return Response(
            {"error": "Failed to fetch news categories", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_news(request, category):
    """
    Belirli bir kategorideki haberleri listeler
    """
    try:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        news_data = news_service.get_category_news(category, page=page, page_size=page_size)
        
        # Error kontrolü
        if 'error' in news_data:
            return Response(
                {"error": news_data['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(news_data)
        
    except Exception as e:
        logger.error(f"Error in category_news view for category {category}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch news for category {category}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_news(request, symbol):
    """
    Belirli bir hisse senedi ile ilgili haberleri listeler
    """
    try:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        days_back = int(request.query_params.get('days_back', 7))
        
        # Sembolün geçerli olup olmadığını kontrol et
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
        except Stock.DoesNotExist:
            pass  # Veritabanında yoksa bile haberleri çekmeye çalış
        
        news_data = news_service.get_stock_specific_news(
            symbol.upper(), 
            days_back=days_back,
            page=page, 
            page_size=page_size
        )
        
        # Error kontrolü
        if 'error' in news_data:
            return Response(
                {"error": news_data['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Haber verilerine duygu analizi ekle
        if 'articles' in news_data and news_data['articles']:
            sentiment_results = sentiment_analyzer.analyze_articles(news_data['articles'])
            
            # Her habere duygu analizi sonucu ekle
            for i, article in enumerate(news_data['articles']):
                if i < len(sentiment_results.get('articles', [])):
                    article['sentiment'] = sentiment_results['articles'][i]['sentiment']
            
            # Toplam duygu analizi istatistikleri
            news_data['sentiment_summary'] = {
                'sentiment_counts': sentiment_results.get('sentiment_counts', {}),
                'average_scores': sentiment_results.get('average_scores', {})
            }
        
        return Response(news_data)
        
    except Exception as e:
        logger.error(f"Error in stock_news view for symbol {symbol}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch news for {symbol}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sentiment_analysis(request):
    """
    Haber metinleri için duygu analizi yapar
    """
    try:
        symbol = request.query_params.get('symbol')
        days_back = int(request.query_params.get('days_back', 7))
        
        if not symbol:
            return Response(
                {"error": "Symbol parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Hisse haberleri al
        news_data = news_service.get_stock_specific_news(
            symbol.upper(), 
            days_back=days_back,
            page=1, 
            page_size=50  # Daha fazla haber al
        )
        
        if 'error' in news_data:
            return Response(
                {"error": news_data['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Duygu analizi yap
        articles = news_data.get('articles', [])
        
        if not articles:
            return Response(
                {"error": f"No news found for {symbol} in the last {days_back} days"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sentiment_results = sentiment_analyzer.analyze_articles(articles)
        
        # Görselleştirme ekle
        try:
            # Duygu dağılımı grafiği
            visualizer = SentimentDistributionVisualizer()
            distribution_chart = visualizer.generate_visualization(sentiment_results['sentiment_counts'])
            
            # Zaman serisi grafiği
            time_series_visualizer = SentimentTimeSeriesVisualizer()
            trends_data = sentiment_analyzer.analyze_sentiment_trends(articles)
            trend_chart = time_series_visualizer.generate_visualization(trends_data.get('trends', []))
            
            # Görselleştirmeleri ekle
            sentiment_results['visualizations'] = {
                'distribution_chart': distribution_chart,
                'trend_chart': trend_chart
            }
        except Exception as viz_error:
            logger.error(f"Error generating visualizations: {str(viz_error)}")
            sentiment_results['visualizations'] = None
        
        # Sonuçları formatla
        response = {
            'symbol': symbol,
            'period': f"Last {days_back} days",
            'articles_analyzed': len(articles),
            'sentiment_summary': {
                'sentiment_counts': sentiment_results.get('sentiment_counts', {}),
                'average_scores': sentiment_results.get('average_scores', {})
            },
            'articles': [
                {
                    'title': article['title'],
                    'url': article['url'],
                    'published_at': article['published_at'],
                    'sentiment': sentiment['sentiment']
                }
                for article, sentiment in zip(articles, sentiment_results.get('articles', []))
            ],
            'visualizations': sentiment_results.get('visualizations')
        }
        
        return Response(response)
        
    except Exception as e:
        logger.error(f"Error in sentiment_analysis view: {str(e)}")
        return Response(
            {"error": "Failed to perform sentiment analysis", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sentiment_trends(request):
    """
    Zaman içindeki duygu trendlerini gösterir
    """
    try:
        symbol = request.query_params.get('symbol')
        days_back = int(request.query_params.get('days_back', 30))
        
        if not symbol:
            return Response(
                {"error": "Symbol parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Hisse haberleri al
        news_data = news_service.get_stock_specific_news(
            symbol.upper(), 
            days_back=days_back,
            page=1, 
            page_size=100  # Daha fazla haber al
        )
        
        if 'error' in news_data:
            return Response(
                {"error": news_data['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        articles = news_data.get('articles', [])
        
        if not articles:
            return Response(
                {"error": f"No news found for {symbol} in the last {days_back} days"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Duygu trendi analizi
        trends_data = sentiment_analyzer.analyze_sentiment_trends(articles)
        
        # Görselleştirme
        visualizer = SentimentTimeSeriesVisualizer()
        chart = visualizer.generate_visualization(trends_data.get('trends', []))
        
        # Sonuç
        response = {
            'symbol': symbol,
            'period': f"Last {days_back} days",
            'total_articles': trends_data.get('total_articles', 0),
            'trends': trends_data.get('trends', []),
            'chart': chart
        }
        
        return Response(response)
        
    except Exception as e:
        logger.error(f"Error in sentiment_trends view: {str(e)}")
        return Response(
            {"error": "Failed to fetch sentiment trends", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_news(request):
    """
    Haber araması yapar
    """
    try:
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Tarih aralığı parametreleri
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Haber araması yap
        news_data = news_service.search_news(
            query=query,
            from_date=from_date,
            to_date=to_date,
            page=page,
            page_size=page_size
        )
        
        # Error kontrolü
        if 'error' in news_data:
            return Response(
                {"error": news_data['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(news_data)
        
    except Exception as e:
        logger.error(f"Error in search_news view: {str(e)}")
        return Response(
            {"error": "Failed to search news", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_preferences(request):
    """
    Kullanıcının haber tercihlerini getirir
    """
    try:
        user = request.user
        
        # Kullanıcı tercihlerini al veya oluştur
        preferences, created = UserPreference.objects.get_or_create(user=user)
        
        return Response({
            'preferred_news_categories': preferences.preferred_news_categories,
            'email_notifications': preferences.email_notifications,
            'sms_notifications': preferences.sms_notifications
        })
        
    except Exception as e:
        logger.error(f"Error in news_preferences view: {str(e)}")
        return Response(
            {"error": "Failed to fetch news preferences", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_news_preferences(request):
    """
    Kullanıcının haber tercihlerini günceller
    """
    try:
        user = request.user
        data = request.data
        
        # Tercihleri kontrol et
        preferred_news_categories = data.get('preferred_news_categories')
        email_notifications = data.get('email_notifications')
        sms_notifications = data.get('sms_notifications')
        
        # Kullanıcı tercihlerini güncelle
        preferences, created = UserPreference.objects.get_or_create(user=user)
        
        if preferred_news_categories is not None:
            preferences.preferred_news_categories = preferred_news_categories
        
        if email_notifications is not None:
            preferences.email_notifications = email_notifications
        
        if sms_notifications is not None:
            preferences.sms_notifications = sms_notifications
            
        preferences.save()
        
        return Response({
            'status': 'success',
            'message': 'News preferences updated successfully',
            'preferences': {
                'preferred_news_categories': preferences.preferred_news_categories,
                'email_notifications': preferences.email_notifications,
                'sms_notifications': preferences.sms_notifications
            }
        })
        
    except Exception as e:
        logger.error(f"Error in update_news_preferences view: {str(e)}")
        return Response(
            {"error": "Failed to update news preferences", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
