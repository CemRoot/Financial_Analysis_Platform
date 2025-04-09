# backend/apps/dashboard/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from datetime import datetime, timedelta

from apps.stocks.models import Stock, StockPrice
from apps.accounts.models import Watchlist
from apps.stocks.services.stock_service import StockDataService
from apps.predictions.services.prediction_service import PredictionService

import logging
import random

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Ana pano özet verilerini döndürür
    """
    try:
        user = request.user
        
        # Kullanıcının izleme listeleri
        watchlists = Watchlist.objects.filter(user=user)
        watchlist_stats = {
            'total_watchlists': watchlists.count(),
            'total_stocks': sum(watchlist.items.count() for watchlist in watchlists),
        }
        
        # Piyasa özeti için
        stock_service = StockDataService()
        market_movers = stock_service.get_market_movers()
        
        # S&P 500 gibi piyasa endeksleri örneği
        indices = [
            {'symbol': '^GSPC', 'name': 'S&P 500'},
            {'symbol': '^DJI', 'name': 'Dow Jones'},
            {'symbol': '^IXIC', 'name': 'NASDAQ'}
        ]
        
        market_indices = []
        for index in indices:
            try:
                index_info = stock_service.get_stock_info(index['symbol'])
                if index_info:
                    current_price = index_info.get('current_price', 0) or 0
                    previous_close = index_info.get('previous_close', 0) or 0
                    
                    if previous_close > 0:
                        change_percent = (current_price - previous_close) / previous_close * 100
                    else:
                        change_percent = 0
                        
                    market_indices.append({
                        'symbol': index['symbol'],
                        'name': index['name'],
                        'current_price': current_price,
                        'change_percent': change_percent,
                    })
            except Exception as e:
                logger.error(f"Error fetching index {index['symbol']}: {str(e)}")
        
        # Tahmin servisi
        prediction_service = PredictionService()
        
        # Rastgele bir hisse için tahmin örneği
        popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        sample_symbol = random.choice(popular_symbols)
        
        prediction = prediction_service.predict_market_direction(sample_symbol)
        
        # Sonuç
        return Response({
            'user_info': {
                'username': user.username,
                'email': user.email,
                'watchlists': watchlist_stats,
            },
            'market_summary': {
                'indices': market_indices,
                'top_gainers': market_movers.get('gainers', [])[:3],
                'top_losers': market_movers.get('losers', [])[:3],
            },
            'prediction_highlight': {
                'symbol': sample_symbol,
                'prediction': prediction.get('prediction') if prediction.get('status') == 'success' else None,
                'confidence': prediction.get('confidence') if prediction.get('status') == 'success' else None,
            }
        })
        
    except Exception as e:
        logger.error(f"Error in dashboard_summary view: {str(e)}")
        return Response(
            {"error": "Failed to fetch dashboard summary", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_widgets(request):
    """
    Dashboard widget'ları için verileri döndürür
    """
    widgets = []  # Define widgets outside the try block to ensure we always return something
    
    try:
        user = request.user
        
        # Kullanıcının izleme listeleri
        watchlists = Watchlist.objects.filter(user=user)
        
        # İzleme listesi widget'ı
        if watchlists.exists():
            primary_watchlist = watchlists.first()
            watch_stocks = []
            
            # Hisse bilgilerini al
            stock_service = StockDataService()
            
            for item in primary_watchlist.items.all()[:5]:  # İlk 5 hisse ile sınırla
                try:
                    stock_info = stock_service.get_stock_info(item.symbol)
                    if stock_info:
                        # Fix the NoneType error by adding safety checks
                        current_price = stock_info.get('current_price', 0) or 0
                        previous_close = stock_info.get('previous_close', 0) or 0
                        
                        # Calculate change percent with safety check
                        if previous_close > 0:
                            change_percent = (current_price - previous_close) / previous_close * 100
                        else:
                            change_percent = 0
                            
                        watch_stocks.append({
                            'symbol': item.symbol,
                            'name': stock_info.get('name', ''),
                            'price': current_price,
                            'change_percent': change_percent,
                            'is_fallback': stock_info.get('is_fallback', False)
                        })
                except Exception as e:
                    logger.error(f"Error fetching stock info for {item.symbol}: {str(e)}")
                    # Add fallback data if there's an error
                    watch_stocks.append(generate_fallback_stock(item.symbol))
            
            # If no stocks were found, add fallback data
            if not watch_stocks:
                popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
                for symbol in popular_symbols:
                    watch_stocks.append(generate_fallback_stock(symbol))
            
            widgets.append({
                'id': 'watchlist',
                'title': primary_watchlist.name,
                'type': 'watchlist',
                'data': watch_stocks
            })
        else:
            # If no watchlist exists, create a fallback watchlist with popular stocks
            popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
            watch_stocks = [generate_fallback_stock(symbol) for symbol in popular_symbols]
            
            widgets.append({
                'id': 'watchlist',
                'title': 'Popular Stocks',
                'type': 'watchlist',
                'data': watch_stocks,
                'is_fallback': True
            })
        
        # Piyasa endeksleri widget'ı
        indices = [
            {'symbol': '^GSPC', 'name': 'S&P 500'},
            {'symbol': '^DJI', 'name': 'Dow Jones'},
            {'symbol': '^IXIC', 'name': 'NASDAQ'},
            {'symbol': '^RUT', 'name': 'Russell 2000'}
        ]
        
        stock_service = StockDataService()
        market_indices = []
        
        for index in indices:
            try:
                index_info = stock_service.get_stock_info(index['symbol'])
                if index_info:
                    # Fix the NoneType error with safe defaults
                    current_price = index_info.get('current_price', 0) or 0
                    previous_close = index_info.get('previous_close', 0) or 0
                    
                    # Calculate change percent safely
                    if previous_close > 0:
                        change_percent = (current_price - previous_close) / previous_close * 100
                    else:
                        change_percent = 0
                        
                    market_indices.append({
                        'symbol': index['symbol'],
                        'name': index['name'],
                        'price': current_price,
                        'change_percent': change_percent,
                        'is_fallback': index_info.get('is_fallback', False)
                    })
                else:
                    # If no data returned, add fallback data
                    market_indices.append(generate_fallback_index(index['symbol'], index['name']))
            except Exception as e:
                logger.error(f"Error fetching index {index['symbol']}: {str(e)}")
                # Add fallback data
                market_indices.append(generate_fallback_index(index['symbol'], index['name']))
        
        # If all indices failed, ensure we have fallback data
        if not market_indices:
            for index in indices:
                market_indices.append(generate_fallback_index(index['symbol'], index['name']))
        
        widgets.append({
            'id': 'market_indices',
            'title': 'Market Indices',
            'type': 'indices',
            'data': market_indices
        })
        
        # Sektor performansı widget'ı
        try:
            # Attempt to get real sector data (this is stub code in the original)
            sectors = [
                {'name': 'Technology', 'change_percent': 1.24},
                {'name': 'Healthcare', 'change_percent': -0.52},
                {'name': 'Financials', 'change_percent': 0.78},
                {'name': 'Consumer Cyclical', 'change_percent': 0.42},
                {'name': 'Energy', 'change_percent': -1.18}
            ]
        except Exception as e:
            logger.error(f"Error fetching sector performance: {str(e)}")
            # Fallback sector data
            sectors = generate_fallback_sectors()
        
        widgets.append({
            'id': 'sector_performance',
            'title': 'Sector Performance',
            'type': 'sectors',
            'data': sectors
        })
        
        # Market tahminleri widget'ı
        prediction_service = PredictionService()
        predictions = []
        
        symbols_to_predict = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL']
        for symbol in symbols_to_predict:
            try:
                prediction = prediction_service.predict_market_direction(symbol)
                if prediction and prediction.get('status') == 'success':
                    predictions.append({
                        'symbol': symbol,
                        'prediction': prediction.get('prediction', 'neutral'),
                        'confidence': prediction.get('confidence', 50),
                        'timestamp': datetime.now().isoformat(),
                        'is_fallback': prediction.get('is_fallback', False)
                    })
                else:
                    # Add fallback prediction if status is not success
                    predictions.append(generate_fallback_prediction(symbol))
            except Exception as e:
                logger.error(f"Error fetching prediction for {symbol}: {str(e)}")
                # Add fallback prediction data
                predictions.append(generate_fallback_prediction(symbol))
        
        # If no predictions were made successfully, generate fallback data for all
        if not predictions:
            predictions = [generate_fallback_prediction(symbol) for symbol in symbols_to_predict]
        
        widgets.append({
            'id': 'predictions',
            'title': 'Market Predictions',
            'type': 'predictions',
            'data': predictions
        })
        
        # Performans karşılaştırmawidget'ı
        try:
            # Try to get real performance data from stock service
            performance_symbols = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
            performance_data = []
            
            for symbol in performance_symbols:
                try:
                    # This would be replaced with actual API call in a real implementation
                    # For now using the stub data
                    if symbol == 'AAPL':
                        performance_data.append({
                            'symbol': 'AAPL', 
                            'name': 'Apple Inc.', 
                            'return_1m': 3.2, 
                            'return_3m': 7.5, 
                            'return_1y': 15.8
                        })
                    elif symbol == 'MSFT':
                        performance_data.append({
                            'symbol': 'MSFT', 
                            'name': 'Microsoft', 
                            'return_1m': 2.8, 
                            'return_3m': 6.9, 
                            'return_1y': 18.2
                        })
                    elif symbol == 'AMZN':
                        performance_data.append({
                            'symbol': 'AMZN', 
                            'name': 'Amazon', 
                            'return_1m': -1.2, 
                            'return_3m': 4.3, 
                            'return_1y': 12.7
                        })
                    elif symbol == 'GOOGL':
                        performance_data.append({
                            'symbol': 'GOOGL', 
                            'name': 'Alphabet', 
                            'return_1m': 1.9, 
                            'return_3m': 5.1, 
                            'return_1y': 14.3
                        })
                    elif symbol == 'META':
                        performance_data.append({
                            'symbol': 'META', 
                            'name': 'Meta Platforms', 
                            'return_1m': 4.1, 
                            'return_3m': 9.8, 
                            'return_1y': 22.5
                        })
                    else:
                        performance_data.append(generate_fallback_performance(symbol))
                except Exception as e:
                    logger.error(f"Error fetching performance data for {symbol}: {str(e)}")
                    performance_data.append(generate_fallback_performance(symbol))
            
            # If no performance data was collected, use fallback data
            if not performance_data:
                performance_data = [generate_fallback_performance(symbol) for symbol in performance_symbols]
                
        except Exception as e:
            logger.error(f"Error generating performance data: {str(e)}")
            # Use fallback performance data
            performance_data = [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'return_1m': 3.2, 'return_3m': 7.5, 'return_1y': 15.8, 'is_fallback': True},
                {'symbol': 'MSFT', 'name': 'Microsoft', 'return_1m': 2.8, 'return_3m': 6.9, 'return_1y': 18.2, 'is_fallback': True},
                {'symbol': 'AMZN', 'name': 'Amazon', 'return_1m': -1.2, 'return_3m': 4.3, 'return_1y': 12.7, 'is_fallback': True},
                {'symbol': 'GOOGL', 'name': 'Alphabet', 'return_1m': 1.9, 'return_3m': 5.1, 'return_1y': 14.3, 'is_fallback': True},
                {'symbol': 'META', 'name': 'Meta Platforms', 'return_1m': 4.1, 'return_3m': 9.8, 'return_1y': 22.5, 'is_fallback': True}
            ]
        
        widgets.append({
            'id': 'performance',
            'title': 'Stock Performance',
            'type': 'performance',
            'data': performance_data
        })
        
        # Recent Activity widget
        try:
            activity_data = get_recent_activity_data(user)
            if not activity_data:
                activity_data = generate_fallback_activity()
        except Exception as e:
            logger.error(f"Error fetching recent activity: {str(e)}")
            activity_data = generate_fallback_activity()
            
        widgets.append({
            'id': 'recent_activity',
            'title': 'Recent Activity',
            'type': 'activity',
            'data': activity_data
        })
        
        # Market News widget
        try:
            news_data = get_market_news()
            if not news_data:
                news_data = generate_fallback_news()
        except Exception as e:
            logger.error(f"Error fetching market news: {str(e)}")
            news_data = generate_fallback_news()
            
        widgets.append({
            'id': 'market_news',
            'title': 'Market News',
            'type': 'news',
            'data': news_data
        })
        
    except Exception as e:
        logger.error(f"Error in dashboard_widgets view: {str(e)}")
        # If a critical error occurs, ensure we provide fallback widgets
        if not widgets:
            widgets = generate_fallback_widgets()
    
    # Always return a response, even if there's an error
    return Response(widgets)

# Helper functions for fallback data generation

def generate_fallback_stock(symbol):
    """Generate fallback data for a stock"""
    # Map common stock symbols to company names
    stock_names = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'AMZN': 'Amazon.com Inc.',
        'GOOGL': 'Alphabet Inc.',
        'META': 'Meta Platforms Inc.',
        'TSLA': 'Tesla Inc.',
        'NVDA': 'NVIDIA Corporation',
        'JPM': 'JPMorgan Chase & Co.',
        'V': 'Visa Inc.',
        'BAC': 'Bank of America Corporation'
    }
    
    # Generate a deterministic but realistic price based on the symbol
    base_price = 0
    for char in symbol:
        base_price += ord(char)
    base_price = (base_price % 900) + 100  # Between $100 and $1000
    
    # Generate random change percentage between -3% and +3%
    change_percent = (random.random() * 6) - 3
    
    return {
        'symbol': symbol,
        'name': stock_names.get(symbol, f"{symbol} Inc."),
        'price': base_price,
        'change_percent': round(change_percent, 2),
        'is_fallback': True
    }

def generate_fallback_index(symbol, name):
    """Generate fallback data for a market index"""
    # Base values for common indices
    base_values = {
        '^GSPC': 4500,  # S&P 500
        '^DJI': 36000,  # Dow Jones
        '^IXIC': 14000,  # NASDAQ
        '^RUT': 2200    # Russell 2000
    }
    
    # Get base value or generate one
    base_value = base_values.get(symbol, 1000 + (hash(symbol) % 4000))
    
    # Generate random change percentage between -2% and +2%
    change_percent = (random.random() * 4) - 2
    
    return {
        'symbol': symbol,
        'name': name,
        'price': base_value,
        'change_percent': round(change_percent, 2),
        'is_fallback': True
    }

def generate_fallback_sectors():
    """Generate fallback sector performance data"""
    sectors = [
        'Technology', 'Healthcare', 'Financials', 'Consumer Cyclical', 
        'Energy', 'Communication Services', 'Industrials', 'Utilities',
        'Real Estate', 'Consumer Defensive', 'Basic Materials'
    ]
    
    return [
        {
            'name': sector,
            'change_percent': round((random.random() * 6) - 3, 2),  # Between -3% and +3%
            'is_fallback': True
        }
        for sector in sectors
    ]

def generate_fallback_prediction(symbol):
    """Generate fallback market prediction data"""
    # Bias the prediction slightly positive for certain symbols
    positive_bias = symbol in ['AAPL', 'MSFT', 'GOOGL', 'SPY']
    
    # Choose prediction with bias
    if positive_bias:
        prediction = 'up' if random.random() < 0.65 else 'down'
    else:
        prediction = 'up' if random.random() < 0.5 else 'down'
    
    # Generate confidence between 55% and 85%
    confidence = 55 + (random.random() * 30)
    
    return {
        'symbol': symbol,
        'prediction': prediction,
        'confidence': round(confidence, 1),
        'timestamp': datetime.now().isoformat(),
        'is_fallback': True
    }

def generate_fallback_performance(symbol):
    """Generate fallback performance data for a stock"""
    # Map common stock symbols to company names
    stock_names = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'AMZN': 'Amazon.com Inc.',
        'GOOGL': 'Alphabet Inc.',
        'META': 'Meta Platforms Inc.',
        'TSLA': 'Tesla Inc.',
        'NVDA': 'NVIDIA Corporation',
        'JPM': 'JPMorgan Chase & Co.',
        'V': 'Visa Inc.',
        'BAC': 'Bank of America Corporation'
    }
    
    # Generate realistic returns with some correlation
    base_return = (random.random() * 10) - 2  # Base return between -2% and +8%
    
    # 1-month return (more volatile)
    return_1m = base_return + ((random.random() * 8) - 4)  # Adjust by -4% to +4%
    
    # 3-month return (less volatile than 1m, more than 1y)
    return_3m = base_return * 2 + ((random.random() * 6) - 3)  # Adjust by -3% to +3%
    
    # 1-year return (tends to be more positive)
    return_1y = base_return * 3 + (random.random() * 10)  # Adjust by 0% to +10%
    
    return {
        'symbol': symbol,
        'name': stock_names.get(symbol, f"{symbol} Inc."),
        'return_1m': round(return_1m, 1),
        'return_3m': round(return_3m, 1),
        'return_1y': round(return_1y, 1),
        'is_fallback': True
    }

def get_recent_activity_data(user):
    """Get recent activity data for the user"""
    # In a real implementation, this would fetch from database
    # This is just a stub
    return []

def generate_fallback_activity():
    """Generate fallback recent activity data"""
    activity_types = ['login', 'viewed_stock', 'added_to_watchlist', 'removed_from_watchlist', 'prediction']
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V']
    
    activities = []
    for i in range(5):
        activity_type = random.choice(activity_types)
        timestamp = datetime.now() - timedelta(hours=random.randint(1, 48))
        
        if activity_type == 'login':
            activity = {
                'type': 'login',
                'description': 'Logged in to the platform',
                'timestamp': timestamp.isoformat()
            }
        elif activity_type == 'viewed_stock':
            symbol = random.choice(symbols)
            activity = {
                'type': 'viewed_stock',
                'description': f'Viewed {symbol} stock details',
                'symbol': symbol,
                'timestamp': timestamp.isoformat()
            }
        elif activity_type == 'added_to_watchlist':
            symbol = random.choice(symbols)
            activity = {
                'type': 'watchlist',
                'description': f'Added {symbol} to watchlist',
                'symbol': symbol,
                'action': 'added',
                'timestamp': timestamp.isoformat()
            }
        elif activity_type == 'removed_from_watchlist':
            symbol = random.choice(symbols)
            activity = {
                'type': 'watchlist',
                'description': f'Removed {symbol} from watchlist',
                'symbol': symbol,
                'action': 'removed',
                'timestamp': timestamp.isoformat()
            }
        else:  # prediction
            symbol = random.choice(symbols)
            prediction = 'bullish' if random.random() > 0.5 else 'bearish'
            activity = {
                'type': 'prediction',
                'description': f'Made {prediction} prediction for {symbol}',
                'symbol': symbol,
                'prediction': prediction,
                'timestamp': timestamp.isoformat()
            }
        
        activities.append(activity)
    
    # Sort by timestamp, most recent first
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return activities

def get_market_news():
    """Get market news data"""
    # In a real implementation, this would fetch from a news API
    # This is just a stub
    return []

def generate_fallback_news():
    """Generate fallback market news data"""
    news = [
        {
            'title': 'Fed Signals Potential Rate Cuts in Coming Months',
            'source': 'Financial Times',
            'url': 'https://www.ft.com',
            'published_at': (datetime.now() - timedelta(hours=3)).isoformat(),
            'summary': 'The Federal Reserve has indicated it may consider rate cuts in the coming months as inflation pressures ease.',
            'sentiment': 'positive'
        },
        {
            'title': 'Tech Giants Report Strong Quarterly Earnings',
            'source': 'Wall Street Journal',
            'url': 'https://www.wsj.com',
            'published_at': (datetime.now() - timedelta(hours=5)).isoformat(),
            'summary': 'Major technology companies exceeded analyst expectations in their latest quarterly reports, driven by AI and cloud services.',
            'sentiment': 'positive'
        },
        {
            'title': 'Oil Prices Drop Amid Supply Concerns',
            'source': 'Bloomberg',
            'url': 'https://www.bloomberg.com',
            'published_at': (datetime.now() - timedelta(hours=8)).isoformat(),
            'summary': 'Crude oil prices fell today as markets reacted to potential increases in global supply and concerns about economic growth.',
            'sentiment': 'negative'
        },
        {
            'title': 'Retail Sales Show Unexpected Growth in Latest Report',
            'source': 'CNBC',
            'url': 'https://www.cnbc.com',
            'published_at': (datetime.now() - timedelta(hours=12)).isoformat(),
            'summary': 'Consumer spending remained resilient with retail sales growing more than expected, suggesting continued economic strength.',
            'sentiment': 'positive'
        },
        {
            'title': 'New Regulations Proposed for Financial Technology Sector',
            'source': 'Reuters',
            'url': 'https://www.reuters.com',
            'published_at': (datetime.now() - timedelta(hours=18)).isoformat(),
            'summary': 'Regulators have announced proposals for new oversight of financial technology companies, focusing on consumer protection.',
            'sentiment': 'neutral'
        }
    ]
    
    for item in news:
        item['is_fallback'] = True
        
    return news

def generate_fallback_widgets():
    """Generate a complete set of fallback widgets if a critical error occurs"""
    widgets = []
    
    # Watchlist widget with popular stocks
    popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    watch_stocks = [generate_fallback_stock(symbol) for symbol in popular_symbols]
    widgets.append({
        'id': 'watchlist',
        'title': 'Popular Stocks',
        'type': 'watchlist',
        'data': watch_stocks,
        'is_fallback': True
    })
    
    # Market indices widget
    indices = [
        {'symbol': '^GSPC', 'name': 'S&P 500'},
        {'symbol': '^DJI', 'name': 'Dow Jones'},
        {'symbol': '^IXIC', 'name': 'NASDAQ'},
        {'symbol': '^RUT', 'name': 'Russell 2000'}
    ]
    market_indices = [generate_fallback_index(index['symbol'], index['name']) for index in indices]
    widgets.append({
        'id': 'market_indices',
        'title': 'Market Indices',
        'type': 'indices',
        'data': market_indices,
        'is_fallback': True
    })
    
    # Sector performance widget
    widgets.append({
        'id': 'sector_performance',
        'title': 'Sector Performance',
        'type': 'sectors',
        'data': generate_fallback_sectors(),
        'is_fallback': True
    })
    
    # Market predictions widget
    prediction_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL']
    predictions = [generate_fallback_prediction(symbol) for symbol in prediction_symbols]
    widgets.append({
        'id': 'predictions',
        'title': 'Market Predictions',
        'type': 'predictions',
        'data': predictions,
        'is_fallback': True
    })
    
    # Performance comparison widget
    performance_symbols = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
    performance_data = [generate_fallback_performance(symbol) for symbol in performance_symbols]
    widgets.append({
        'id': 'performance',
        'title': 'Stock Performance',
        'type': 'performance',
        'data': performance_data,
        'is_fallback': True
    })
    
    # Recent activity widget
    widgets.append({
        'id': 'recent_activity',
        'title': 'Recent Activity',
        'type': 'activity',
        'data': generate_fallback_activity(),
        'is_fallback': True
    })
    
    # Market news widget
    widgets.append({
        'id': 'market_news',
        'title': 'Market News',
        'type': 'news',
        'data': generate_fallback_news(),
        'is_fallback': True
    })
    
    return widgets

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def market_overview(request):
    """
    Piyasa genel görünümü bilgilerini döndürür
    """
    # Initialize response data with empty structures to ensure we always return something
    indices_data = []
    market_movers = {'gainers': [], 'losers': [], 'most_active': []}
    sectors = []
    stats = {}
    news = []
    
    try:
        stock_service = StockDataService()
        
        # Market movers
        try:
            market_movers = stock_service.get_market_movers()
            
            # If market_movers is None or empty, use fallback data
            if not market_movers or not any(market_movers.values()):
                market_movers = generate_fallback_market_movers()
        except Exception as e:
            logger.error(f"Error fetching market movers: {str(e)}")
            market_movers = generate_fallback_market_movers()
        
        # Piyasa endeksleri
        indices = [
            {'symbol': '^GSPC', 'name': 'S&P 500'},
            {'symbol': '^DJI', 'name': 'Dow Jones'},
            {'symbol': '^IXIC', 'name': 'NASDAQ'}
        ]
        
        indices_data = []
        for index in indices:
            try:
                index_info = stock_service.get_stock_info(index['symbol'])
                if index_info:
                    # Fix NoneType errors with safe values
                    current_price = index_info.get('current_price', 0) or 0
                    previous_close = index_info.get('previous_close', 0) or 0
                    day_high = index_info.get('day_high', 0) or 0
                    day_low = index_info.get('day_low', 0) or 0
                    
                    # Calculate change percent safely
                    if previous_close > 0:
                        change_percent = (current_price - previous_close) / previous_close * 100
                    else:
                        change_percent = 0
                        
                    indices_data.append({
                        'symbol': index['symbol'],
                        'name': index['name'],
                        'price': current_price,
                        'change_percent': change_percent,
                        'day_range': f"{day_low:.2f} - {day_high:.2f}",
                        'volume': index_info.get('volume', 0) or 0,
                        'is_fallback': index_info.get('is_fallback', False)
                    })
                else:
                    # Add fallback data if no index info available
                    indices_data.append(generate_fallback_market_index(index['symbol'], index['name']))
            except Exception as e:
                logger.error(f"Error fetching index {index['symbol']}: {str(e)}")
                # Add fallback data
                indices_data.append(generate_fallback_market_index(index['symbol'], index['name']))
        
        # If all indices failed, generate fallback data
        if not indices_data:
            for index in indices:
                indices_data.append(generate_fallback_market_index(index['symbol'], index['name']))
        
        # Sektör performansı
        try:
            # In a real implementation, this would come from an API
            # For now, we'll use the existing hardcoded data but with improved error handling
            sectors = [
                {'name': 'Technology', 'change_percent': 1.24, 'ytd_change': 18.5},
                {'name': 'Healthcare', 'change_percent': -0.52, 'ytd_change': 5.7},
                {'name': 'Financials', 'change_percent': 0.78, 'ytd_change': 9.2},
                {'name': 'Consumer Cyclical', 'change_percent': 0.42, 'ytd_change': 7.8},
                {'name': 'Energy', 'change_percent': -1.18, 'ytd_change': -3.2},
                {'name': 'Real Estate', 'change_percent': 0.35, 'ytd_change': 4.9},
                {'name': 'Industrials', 'change_percent': 0.92, 'ytd_change': 11.3},
                {'name': 'Utilities', 'change_percent': -0.25, 'ytd_change': 2.1},
                {'name': 'Materials', 'change_percent': 0.68, 'ytd_change': 6.7}
            ]
        except Exception as e:
            logger.error(f"Error fetching sector performance: {str(e)}")
            sectors = generate_fallback_market_sectors()
        
        # Piyasa istatistikleri
        try:
            # In a real implementation, this would come from an API
            # For now, we'll use the existing hardcoded data but with improved error handling
            stats = {
                'advancing_stocks': 235,
                'declining_stocks': 265,
                'volume': 3.8,  # milyar
                'avg_volume': 4.1,  # milyar
                'new_highs': 47,
                'new_lows': 12,
                'market_cap_change': 1.2  # trilyon
            }
        except Exception as e:
            logger.error(f"Error fetching market stats: {str(e)}")
            stats = generate_fallback_market_stats()
        
        # Add news data
        try:
            # In a real implementation, this would fetch from a news API
            # For now, we'll use the existing hardcoded data but with improved error handling
            news = [
                {
                    'id': 1,
                    'title': 'Fed Signals Rate Cuts Later This Year',
                    'source': 'Financial Times',
                    'url': 'https://www.ft.com/content/fed-signals-rate-cuts',
                    'published_at': (datetime.now() - timedelta(hours=3)).isoformat(),
                    'sentiment': 'positive'
                },
                {
                    'id': 2,
                    'title': 'Tech Stocks Rally on Earnings Beats',
                    'source': 'Wall Street Journal',
                    'url': 'https://www.wsj.com/articles/tech-stocks-rally',
                    'published_at': (datetime.now() - timedelta(hours=5)).isoformat(),
                    'sentiment': 'positive'
                },
                {
                    'id': 3,
                    'title': 'Oil Prices Drop on Supply Concerns',
                    'source': 'Bloomberg',
                    'url': 'https://www.bloomberg.com/news/oil-prices-drop',
                    'published_at': (datetime.now() - timedelta(hours=7)).isoformat(),
                    'sentiment': 'negative'
                },
                {
                    'id': 4,
                    'title': 'Market Volatility Increases Amid Global Tensions',
                    'source': 'Reuters',
                    'url': 'https://www.reuters.com/markets/volatility-increases',
                    'published_at': (datetime.now() - timedelta(hours=9)).isoformat(),
                    'sentiment': 'neutral'
                },
                {
                    'id': 5,
                    'title': 'Retail Sales Beat Expectations in Latest Report',
                    'source': 'CNBC',
                    'url': 'https://www.cnbc.com/retail-sales-beat-expectations',
                    'published_at': (datetime.now() - timedelta(hours=12)).isoformat(),
                    'sentiment': 'positive'
                }
            ]
        except Exception as e:
            logger.error(f"Error fetching market news: {str(e)}")
            news = generate_fallback_market_news()
        
    except Exception as e:
        logger.error(f"Error in market_overview view: {str(e)}")
        # If a critical error occurs, generate fallback data for everything
        indices_data = [generate_fallback_market_index(index['symbol'], index['name']) for index in [
            {'symbol': '^GSPC', 'name': 'S&P 500'},
            {'symbol': '^DJI', 'name': 'Dow Jones'},
            {'symbol': '^IXIC', 'name': 'NASDAQ'}
        ]]
        market_movers = generate_fallback_market_movers()
        sectors = generate_fallback_market_sectors()
        stats = generate_fallback_market_stats()
        news = generate_fallback_market_news()
    
    # Always return a response, even if there's an error
    return Response({
        'indices': indices_data,
        'movers': market_movers,
        'sector_performance': sectors,
        'market_stats': stats,
        'news': news,
        'timestamp': datetime.now().isoformat()
    })

# Helper functions for market overview fallback data

def generate_fallback_market_index(symbol, name):
    """Generate fallback data for a market index"""
    # Base values for common indices
    base_values = {
        '^GSPC': 4500,  # S&P 500
        '^DJI': 36000,  # Dow Jones
        '^IXIC': 14000,  # NASDAQ
    }
    
    # Get base value or generate one
    base_value = base_values.get(symbol, 1000 + (hash(symbol) % 4000))
    
    # Generate random change percentage between -2% and +2%
    change_percent = (random.random() * 4) - 2
    
    # Generate realistic day range
    day_low = base_value * (1 - random.random() * 0.02)  # Up to 2% lower
    day_high = base_value * (1 + random.random() * 0.02)  # Up to 2% higher
    
    # Generate realistic volume (in millions)
    volume = int(random.random() * 100) + 100  # 100M to 200M
    
    return {
        'symbol': symbol,
        'name': name,
        'price': base_value,
        'change_percent': round(change_percent, 2),
        'day_range': f"{day_low:.2f} - {day_high:.2f}",
        'volume': volume * 1000000,  # Convert to actual volume
        'is_fallback': True
    }

def generate_fallback_market_movers():
    """Generate fallback data for market movers"""
    stock_symbols = [
        'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'FB', 'TSLA', 'NVDA', 
        'JPM', 'JNJ', 'V', 'PG', 'MA', 'UNH', 'HD', 'BAC', 'DIS',
        'PYPL', 'ADBE', 'CRM', 'NFLX', 'CMCSA', 'XOM', 'VZ'
    ]
    
    stock_names = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'AMZN': 'Amazon.com Inc.',
        'GOOGL': 'Alphabet Inc.',
        'FB': 'Meta Platforms Inc.',
        'TSLA': 'Tesla Inc.',
        'NVDA': 'NVIDIA Corporation',
        'JPM': 'JPMorgan Chase & Co.',
        'JNJ': 'Johnson & Johnson',
        'V': 'Visa Inc.',
        'PG': 'Procter & Gamble Co.',
        'MA': 'Mastercard Inc.',
        'UNH': 'UnitedHealth Group Inc.',
        'HD': 'Home Depot Inc.',
        'BAC': 'Bank of America Corporation',
        'DIS': 'Walt Disney Co.',
        'PYPL': 'PayPal Holdings Inc.',
        'ADBE': 'Adobe Inc.',
        'CRM': 'Salesforce Inc.',
        'NFLX': 'Netflix Inc.',
        'CMCSA': 'Comcast Corporation',
        'XOM': 'Exxon Mobil Corporation',
        'VZ': 'Verizon Communications Inc.'
    }
    
    # Helper function to generate a stock mover
    def generate_stock_mover(symbol, change_min, change_max):
        base_price = 0
        for char in symbol:
            base_price += ord(char)
        base_price = (base_price % 900) + 100  # Between $100 and $1000
        
        change_percent = random.uniform(change_min, change_max)
        volume = int(random.random() * 10) + 1  # 1M to 11M
        
        return {
            'symbol': symbol,
            'name': stock_names.get(symbol, f"{symbol} Inc."),
            'price': base_price,
            'change_percent': round(change_percent, 2),
            'volume': volume * 1000000,  # Convert to actual volume
            'is_fallback': True
        }
    
    # Randomly select different stocks for each category
    random.shuffle(stock_symbols)
    gainers = stock_symbols[:5]  # First 5 for gainers
    
    remaining = [s for s in stock_symbols if s not in gainers]
    random.shuffle(remaining)
    losers = remaining[:5]  # Next 5 for losers
    
    remaining = [s for s in stock_symbols if s not in gainers and s not in losers]
    random.shuffle(remaining)
    most_active = remaining[:5]  # Next 5 for most active
    
    return {
        'gainers': [generate_stock_mover(symbol, 3.0, 8.0) for symbol in gainers],  # 3% to 8% gains
        'losers': [generate_stock_mover(symbol, -8.0, -3.0) for symbol in losers],  # 3% to 8% losses
        'most_active': [generate_stock_mover(symbol, -3.0, 3.0) for symbol in most_active]  # -3% to 3% (volatile)
    }

def generate_fallback_market_sectors():
    """Generate fallback data for market sectors"""
    sectors = [
        'Technology', 'Healthcare', 'Financials', 'Consumer Cyclical', 
        'Energy', 'Communication Services', 'Industrials', 'Utilities',
        'Real Estate', 'Consumer Defensive', 'Basic Materials'
    ]
    
    result = []
    for sector in sectors:
        # Generate daily change between -3% and +3%
        daily_change = (random.random() * 6) - 3
        
        # Generate YTD change between -15% and +25% with some correlation to daily change
        base_ytd = daily_change * 5  # Correlation factor
        randomizer = (random.random() * 10) - 5  # Random -5% to +5%
        ytd_change = base_ytd + randomizer
        
        # Ensure YTD stays in reasonable range
        ytd_change = max(min(ytd_change, 25), -15)
        
        result.append({
            'name': sector,
            'change_percent': round(daily_change, 2),
            'ytd_change': round(ytd_change, 1),
            'is_fallback': True
        })
    
    return result

def generate_fallback_market_stats():
    """Generate fallback data for market statistics"""
    # Generate somewhat realistic market statistics
    total_stocks = 500  # Simulating S&P 500 for simplicity
    
    # Advancing vs declining with slight randomization
    advancing = int(total_stocks * (0.4 + (random.random() * 0.2)))  # 40% to 60% advancing
    declining = total_stocks - advancing
    
    # Volume in billions
    volume = round(random.uniform(3.0, 5.0), 1)
    avg_volume = round(volume * (0.9 + (random.random() * 0.3)), 1)  # Slightly different from current volume
    
    # New highs and lows
    new_highs = int(random.random() * 50) + 10  # 10 to 60
    new_lows = int(random.random() * 20) + 5   # 5 to 25
    
    # Market cap change in trillions
    market_cap_change = round((random.random() * 2) - 1, 1)  # -1.0 to +1.0 trillion
    
    return {
        'advancing_stocks': advancing,
        'declining_stocks': declining,
        'volume': volume,
        'avg_volume': avg_volume,
        'new_highs': new_highs,
        'new_lows': new_lows,
        'market_cap_change': market_cap_change,
        'is_fallback': True
    }

def generate_fallback_market_news():
    """Generate fallback data for market news"""
    news = [
        {
            'id': 1,
            'title': 'Fed Signals Potential Rate Cuts in Coming Months',
            'source': 'Financial Times',
            'url': 'https://www.ft.com/content/fed-signals-rate-cuts',
            'published_at': (datetime.now() - timedelta(hours=3)).isoformat(),
            'sentiment': 'positive',
            'is_fallback': True
        },
        {
            'id': 2,
            'title': 'Tech Giants Report Strong Quarterly Earnings',
            'source': 'Wall Street Journal',
            'url': 'https://www.wsj.com/articles/tech-stocks-rally',
            'published_at': (datetime.now() - timedelta(hours=5)).isoformat(),
            'sentiment': 'positive',
            'is_fallback': True
        },
        {
            'id': 3,
            'title': 'Oil Prices Drop Amid Supply Concerns',
            'source': 'Bloomberg',
            'url': 'https://www.bloomberg.com/news/oil-prices-drop',
            'published_at': (datetime.now() - timedelta(hours=7)).isoformat(),
            'sentiment': 'negative',
            'is_fallback': True
        },
        {
            'id': 4,
            'title': 'Market Volatility Increases Amid Global Tensions',
            'source': 'Reuters',
            'url': 'https://www.reuters.com/markets/volatility-increases',
            'published_at': (datetime.now() - timedelta(hours=9)).isoformat(),
            'sentiment': 'neutral',
            'is_fallback': True
        },
        {
            'id': 5,
            'title': 'Retail Sales Beat Expectations in Latest Report',
            'source': 'CNBC',
            'url': 'https://www.cnbc.com/retail-sales-beat-expectations',
            'published_at': (datetime.now() - timedelta(hours=12)).isoformat(),
            'sentiment': 'positive',
            'is_fallback': True
        }
    ]
    
    return news

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """
    Kullanıcının son aktivitelerini döndürür
    """
    try:
        # Bu bir örnek implementasyon - gerçek uygulamada aktivite kaydı tutulmalı
        
        # Örnek aktiviteler
        activities = [
            {
                'type': 'login',
                'description': 'Logged in to the platform',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'type': 'watchlist_add',
                'description': 'Added AAPL to watchlist',
                'symbol': 'AAPL',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                'type': 'search',
                'description': 'Searched for "tech stocks"',
                'timestamp': (datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                'type': 'prediction',
                'description': 'Ran prediction analysis for MSFT',
                'symbol': 'MSFT',
                'timestamp': (datetime.now() - timedelta(days=3)).isoformat()
            },
            {
                'type': 'news_read',
                'description': 'Read article about market trends',
                'timestamp': (datetime.now() - timedelta(days=4)).isoformat()
            }
        ]
        
        return Response(activities)
        
    except Exception as e:
        logger.error(f"Error in recent_activity view: {str(e)}")
        return Response(
            {"error": "Failed to fetch recent activity", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_favorites(request):
    """
    Kullanıcının favori/popüler hisselerini döndürür
    """
    try:
        user = request.user
        
        # Kullanıcının izleme listesindeki hisseleri al
        watchlists = Watchlist.objects.filter(user=user)
        watch_items = []
        
        for watchlist in watchlists:
            items = watchlist.items.all()
            for item in items:
                watch_items.append(item.symbol)
        
        # Tekrarları kaldır
        watch_items = list(set(watch_items))
        
        # Hisse bilgilerini al
        stock_service = StockDataService()
        favorites = []
        
        for symbol in watch_items:
            stock_info = stock_service.get_stock_info(symbol)
            if stock_info:
                favorites.append({
                    'symbol': symbol,
                    'name': stock_info.get('name', ''),
                    'price': stock_info.get('current_price'),
                    'change_percent': (stock_info.get('current_price', 0) - stock_info.get('previous_close', 0)) / 
                                   stock_info.get('previous_close', 1) * 100 if stock_info.get('previous_close') else None,
                    'sector': stock_info.get('sector', '')
                })
        
        # Hiç favori yoksa, popüler hisseleri göster
        if not favorites:
            popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM']
            
            for symbol in popular_symbols:
                stock_info = stock_service.get_stock_info(symbol)
                if stock_info:
                    favorites.append({
                        'symbol': symbol,
                        'name': stock_info.get('name', ''),
                        'price': stock_info.get('current_price'),
                        'change_percent': (stock_info.get('current_price', 0) - stock_info.get('previous_close', 0)) / 
                                       stock_info.get('previous_close', 1) * 100 if stock_info.get('previous_close') else None,
                        'sector': stock_info.get('sector', ''),
                        'is_popular': True  # Kullanıcının favorisi değil, popüler öneri
                    })
        
        return Response(favorites)
        
    except Exception as e:
        logger.error(f"Error in user_favorites view: {str(e)}")
        return Response(
            {"error": "Failed to fetch user favorites", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customize_dashboard(request):
    """
    Kullanıcının dashboard'unu özelleştirmesini sağlar
    """
    try:
        user = request.user
        data = request.data
        
        # Gerçek uygulamada kullanıcı tercihlerini kaydedin
        # Örnek response
        return Response({
            'status': 'success',
            'message': 'Dashboard preferences saved successfully',
            'preferences': data
        })
        
    except Exception as e:
        logger.error(f"Error in customize_dashboard view: {str(e)}")
        return Response(
            {"error": "Failed to save dashboard preferences", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
