# backend/apps/stocks/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings

from .models import Stock, StockPrice, TechnicalIndicator, MarketIndex, StockAlert
from apps.accounts.models import Watchlist, WatchlistItem
from .services.stock_service import StockDataService

import logging

logger = logging.getLogger(__name__)
stock_service = StockDataService()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_list(request):
    """
    Tüm hisse senetlerini veya arama sorgusuna göre filtrelenmiş listeyi döndürür
    """
    try:
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 20))
        
        # Veritabanından hisse senetlerini sorgula
        if query:
            stocks = Stock.objects.filter(
                Q(symbol__icontains=query) | 
                Q(name__icontains=query)
            )[:limit]
        else:
            stocks = Stock.objects.all()[:limit]
            
        # Sonuçları formatlayıp döndür
        results = []
        for stock in stocks:
            try:
                # YFinance API'den güncel verileri al
                stock_info = stock_service.get_stock_info(stock.symbol)
                
                if not stock_info:
                    # API verileri alınamazsa, veritabanı verilerini kullan
                    last_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
                    price_info = {
                        'current_price': float(last_price.close) if last_price else None,
                        'price_change': None,
                        'change_percent': None,
                        'date': last_price.date.isoformat() if last_price else None
                    }
                    
                    # Değişim yüzdesini hesapla
                    if last_price:
                        prev_price = StockPrice.objects.filter(
                            stock=stock, date__lt=last_price.date
                        ).order_by('-date').first()
                        
                        if prev_price:
                            price_change = float(last_price.close) - float(prev_price.close)
                            price_change_percent = (price_change / float(prev_price.close)) * 100
                            price_info['price_change'] = price_change
                            price_info['change_percent'] = price_change_percent
                            
                    # Market status bilgisi ekle (veritabanından geliyorsa bilinmiyor)
                    market_status = None
                else:
                    # API'den gelen verileri kullan
                    price_info = {
                        'current_price': stock_info.get('current_price'),
                        'price_change': stock_info.get('price_change'),
                        'change_percent': stock_info.get('change_percent'),
                        'date': stock_info.get('last_updated')
                    }
                    # Market status bilgisini ekle
                    market_status = stock_info.get('market_status')
                
                # Sonuç sözlüğünü oluştur
                stock_data = {
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'sector': stock.sector,
                    'industry': stock.industry,
                    'current_price': price_info['current_price'],
                    'price_change': price_info['price_change'],
                    'change_percent': price_info['change_percent'],
                    'market_cap': stock_info.get('market_cap') if stock_info else None,
                    'market_status': market_status
                }
                results.append(stock_data)
                
            except Exception as e:
                logger.error(f"Error processing stock {stock.symbol}: {str(e)}")
                continue
        
        return Response(results)
    
    except Exception as e:
        logger.error(f"Error in stock_list view: {str(e)}")
        return Response(
            {"error": "Failed to fetch stock list", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_detail(request, symbol):
    """
    Belirli bir hisse senedinin detay bilgilerini döndürür
    """
    try:
        # Veritabanında hisseyi ara
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
            stock_exists = True
        except Stock.DoesNotExist:
            # Veritabanında yoksa, API'den çek
            stock_exists = False
        
        # YFinance API'den güncel verileri al
        stock_info = stock_service.get_stock_info(symbol.upper())
        
        if not stock_info:
            return Response(
                {"error": f"Could not find stock with symbol: {symbol}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Eğer veritabanında yoksa, ekle
        if not stock_exists:
            stock = Stock(
                symbol=symbol.upper(),
                name=stock_info.get('name', ''),
                sector=stock_info.get('sector', ''),
                industry=stock_info.get('industry', ''),
                market_cap=stock_info.get('market_cap', None),
                website=stock_info.get('website', ''),
                logo_url=stock_info.get('logo_url', '')
            )
            stock.save()
        
        # Kullanıcının izleme listesinde olup olmadığını kontrol et
        in_watchlist = WatchlistItem.objects.filter(
            watchlist__user=request.user,
            symbol=symbol.upper()
        ).exists()
        
        # Teknik göstergeleri al
        indicators = TechnicalIndicator.objects.filter(stock=stock).order_by('-date').first()
        
        # Sonuç sözlüğünü oluştur
        result = {
            'symbol': stock_info.get('symbol'),
            'name': stock_info.get('name'),
            'sector': stock_info.get('sector'),
            'industry': stock_info.get('industry'),
            'market_cap': stock_info.get('market_cap'),
            'website': stock_info.get('website'),
            'logo_url': stock_info.get('logo_url'),
            
            'current_price': stock_info.get('current_price'),
            'previous_close': stock_info.get('previous_close'),
            'open': stock_info.get('open'),
            'day_high': stock_info.get('day_high'),
            'day_low': stock_info.get('day_low'),
            'volume': stock_info.get('volume'),
            
            'fifty_two_week_high': stock_info.get('fifty_two_week_high'),
            'fifty_two_week_low': stock_info.get('fifty_two_week_low'),
            'pe_ratio': stock_info.get('pe_ratio'),
            'eps': stock_info.get('eps'),
            'dividend_yield': stock_info.get('dividend_yield'),
            'beta': stock_info.get('beta'),
            
            # Add real-time market status information
            'market_status': stock_info.get('market_status', {}),
            
            # Add price change information under consistent keys
            'price_change': stock_info.get('price_change'),
            'change_percent': stock_info.get('change_percent'),
            
            'in_watchlist': in_watchlist,
            
            'technical_indicators': {
                'sma_20': float(indicators.sma_20) if indicators and indicators.sma_20 else None,
                'sma_50': float(indicators.sma_50) if indicators and indicators.sma_50 else None,
                'sma_200': float(indicators.sma_200) if indicators and indicators.sma_200 else None,
                'rsi_14': float(indicators.rsi_14) if indicators and indicators.rsi_14 else None,
                'macd': float(indicators.macd) if indicators and indicators.macd else None,
                'macd_signal': float(indicators.macd_signal) if indicators and indicators.macd_signal else None
            } if indicators else {}
        }
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Error in stock_detail view for {symbol}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch details for {symbol}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historical_data(request, symbol):
    """
    Hisse senedinin tarihsel fiyat verilerini döndürür
    """
    logger.info(f"Historical data requested for symbol: {symbol}")
    logger.info(f"Request headers: {request.headers}")
    logger.info(f"Query parameters: {request.query_params}")
    
    try:
        period = request.query_params.get('period', '1y')
        interval = request.query_params.get('interval', '1d')
        
        logger.info(f"Fetching historical data with period={period}, interval={interval}")
        
        # YFinance API'den verileri al
        data = stock_service.get_historical_data(symbol.upper(), period, interval)
        
        if not data:
            logger.error(f"No historical data found for symbol: {symbol}")
            return Response(
                {"error": f"Could not fetch historical data for: {symbol}"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        logger.info(f"Successfully retrieved historical data for {symbol}, {len(data)} data points")
        return Response(data)
    
    except Exception as e:
        logger.error(f"Error in historical_data view for {symbol}: {str(e)}", exc_info=True)
        return Response(
            {"error": f"Failed to fetch historical data for {symbol}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def market_movers(request):
    """
    En çok yükselen ve düşen hisseleri döndürür
    """
    try:
        # YFinance API'den verileri al
        movers = stock_service.get_market_movers()
        
        if not movers or 'gainers' not in movers or 'losers' not in movers:
            return Response(
                {"error": "Could not fetch market movers data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response(movers)
    
    except Exception as e:
        logger.error(f"Error in market_movers view: {str(e)}")
        return Response(
            {"error": "Failed to fetch market movers", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sector_performance(request):
    """
    Sektörlerin performans verilerini döndürür
    """
    try:
        # Örnek sektör performans verileri (gerçek uygulamada API'den alınacak)
        sectors = [
            {"name": "Technology", "change_percent": 2.1, "market_cap": 9.8},
            {"name": "Healthcare", "change_percent": 1.5, "market_cap": 5.2},
            {"name": "Financials", "change_percent": 0.8, "market_cap": 7.6},
            {"name": "Consumer Discretionary", "change_percent": 0.4, "market_cap": 4.1},
            {"name": "Industrials", "change_percent": -0.3, "market_cap": 3.2},
            {"name": "Energy", "change_percent": -1.2, "market_cap": 2.7},
            {"name": "Materials", "change_percent": -0.5, "market_cap": 1.9},
            {"name": "Utilities", "change_percent": 0.2, "market_cap": 1.4},
            {"name": "Real Estate", "change_percent": -0.8, "market_cap": 1.1}
        ]
        
        # Değişim yüzdesine göre sırala
        sectors.sort(key=lambda x: x['change_percent'], reverse=True)
        
        return Response(sectors)
    
    except Exception as e:
        logger.error(f"Error in sector_performance view: {str(e)}")
        return Response(
            {"error": "Failed to fetch sector performance", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def market_indices(request):
    """
    Piyasa endekslerinin (S&P 500, NASDAQ, Dow Jones vb.) verilerini döndürür
    """
    try:
        indices_symbols = ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow Jones, NASDAQ, Russell 2000
        
        results = []
        for symbol in indices_symbols:
            # YFinance API'den verileri al
            index_info = stock_service.get_stock_info(symbol)
            
            if index_info:
                # Endeks adını ayarla
                name = {
                    '^GSPC': 'S&P 500',
                    '^DJI': 'Dow Jones',
                    '^IXIC': 'NASDAQ',
                    '^RUT': 'Russell 2000'
                }.get(symbol, index_info.get('name', symbol))
                
                # Sonuç sözlüğünü oluştur
                index_data = {
                    'symbol': symbol,
                    'name': name,
                    'current_price': index_info.get('current_price'),
                    'change': None,
                    'change_percent': None
                }
                
                # Değişim hesapla
                if index_info.get('current_price') and index_info.get('previous_close'):
                    change = index_info['current_price'] - index_info['previous_close']
                    change_percent = (change / index_info['previous_close']) * 100
                    index_data['change'] = change
                    index_data['change_percent'] = change_percent
                
                results.append(index_data)
        
        if not results:
            return Response(
                {"error": "Could not fetch market indices data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response(results)
    
    except Exception as e:
        logger.error(f"Error in market_indices view: {str(e)}")
        return Response(
            {"error": "Failed to fetch market indices", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def technical_indicators(request, symbol):
    """
    Hisse senedi için teknik gösterge verilerini döndürür
    """
    try:
        stock = get_object_or_404(Stock, symbol=symbol.upper())
        
        # Tüm teknik göstergeleri al
        indicators = TechnicalIndicator.objects.filter(stock=stock).order_by('-date')[:30]
        
        results = []
        for indicator in indicators:
            results.append({
                'date': indicator.date.isoformat(),
                'sma_20': float(indicator.sma_20) if indicator.sma_20 else None,
                'sma_50': float(indicator.sma_50) if indicator.sma_50 else None,
                'sma_200': float(indicator.sma_200) if indicator.sma_200 else None,
                'ema_12': float(indicator.ema_12) if indicator.ema_12 else None,
                'ema_26': float(indicator.ema_26) if indicator.ema_26 else None,
                'macd': float(indicator.macd) if indicator.macd else None,
                'macd_signal': float(indicator.macd_signal) if indicator.macd_signal else None,
                'macd_histogram': float(indicator.macd_histogram) if indicator.macd_histogram else None,
                'rsi_14': float(indicator.rsi_14) if indicator.rsi_14 else None,
                'stoch_k': float(indicator.stoch_k) if indicator.stoch_k else None,
                'stoch_d': float(indicator.stoch_d) if indicator.stoch_d else None,
                'bollinger_upper': float(indicator.bollinger_upper) if indicator.bollinger_upper else None,
                'bollinger_middle': float(indicator.bollinger_middle) if indicator.bollinger_middle else None,
                'bollinger_lower': float(indicator.bollinger_lower) if indicator.bollinger_lower else None,
                'additional_indicators': indicator.additional_indicators
            })
        
        return Response(results)
    
    except Exception as e:
        logger.error(f"Error in technical_indicators view for {symbol}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch technical indicators for {symbol}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def indicator_detail(request, symbol, indicator):
    """
    Belirli bir teknik göstergenin detaylı verilerini döndürür
    """
    try:
        stock = get_object_or_404(Stock, symbol=symbol.upper())
        
        # İndikatör alanlarını kontrol et
        valid_indicators = [
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 
            'macd', 'macd_signal', 'macd_histogram', 'rsi_14', 
            'stoch_k', 'stoch_d', 'bollinger'
        ]
        
        if indicator not in valid_indicators:
            return Response(
                {"error": f"Invalid indicator: {indicator}. Valid indicators are: {', '.join(valid_indicators)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # İndikatör verilerini al
        indicators = TechnicalIndicator.objects.filter(stock=stock).order_by('-date')[:60]
        
        if not indicators:
            return Response(
                {"error": f"No technical indicator data found for {symbol}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Belirli indikatör için verileri formatlayıp döndür
        results = []
        
        if indicator == 'bollinger':
            # Bollinger bantları için özel format
            for ind in indicators:
                results.append({
                    'date': ind.date.isoformat(),
                    'upper': float(ind.bollinger_upper) if ind.bollinger_upper else None,
                    'middle': float(ind.bollinger_middle) if ind.bollinger_middle else None,
                    'lower': float(ind.bollinger_lower) if ind.bollinger_lower else None
                })
        elif indicator in ['macd', 'macd_signal', 'macd_histogram']:
            # MACD göstergeleri için özel format
            for ind in indicators:
                results.append({
                    'date': ind.date.isoformat(),
                    'macd': float(ind.macd) if ind.macd else None,
                    'signal': float(ind.macd_signal) if ind.macd_signal else None,
                    'histogram': float(ind.macd_histogram) if ind.macd_histogram else None
                })
        else:
            # Diğer göstergeler için standart format
            for ind in indicators:
                value = getattr(ind, indicator, None)
                results.append({
                    'date': ind.date.isoformat(),
                    'value': float(value) if value else None
                })
        
        # Yeni-eskiye göre sıralandığından, tarihe göre sıralamak için tersine çevir
        results.reverse()
        
        return Response({
            'symbol': symbol,
            'indicator': indicator,
            'data': results
        })
    
    except Exception as e:
        logger.error(f"Error in indicator_detail view for {symbol}/{indicator}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch {indicator} data for {symbol}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dividends(request, symbol):
    """
    Hisse senedinin temettü geçmişini döndürür
    """
    try:
        # YFinance API'den verileri al
        stock = yf.Ticker(symbol.upper())
        dividends = stock.dividends
        
        if dividends.empty:
            return Response([])
        
        results = []
        for date, value in zip(dividends.index, dividends.values):
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': float(value)
            })
        
        return Response(results)
    
    except Exception as e:
        logger.error(f"Error in dividends view for {symbol}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch dividend data for {symbol}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_data(request, symbol):
    """
    Hisse senedinin finansal verilerini döndürür
    """
    try:
        # Veritabanından finansal verileri sorgula
        stock = get_object_or_404(Stock, symbol=symbol.upper())
        financials = StockFinancial.objects.filter(stock=stock).order_by('-date')
        
        results = []
        for fin in financials:
            results.append({
                'period': fin.period,
                'year': fin.year,
                'date': fin.date.isoformat(),
                'revenue': fin.revenue,
                'gross_profit': fin.gross_profit,
                'operating_income': fin.operating_income,
                'net_income': fin.net_income,
                'eps': float(fin.eps) if fin.eps else None,
                'pe_ratio': float(fin.pe_ratio) if fin.pe_ratio else None,
                'dividend_yield': float(fin.dividend_yield) if fin.dividend_yield else None,
                'debt_to_equity': float(fin.debt_to_equity) if fin.debt_to_equity else None,
                'peg_ratio': float(fin.peg_ratio) if fin.peg_ratio else None
            })
        
        return Response(results)
    
    except Exception as e:
        logger.error(f"Error in financial_data view for {symbol}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch financial data for {symbol}", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_watchlist(request):
    """
    Kullanıcının izleme listesindeki hisseleri döndürür
    """
    try:
        user = request.user
        
        # Kullanıcının tüm izleme listelerini al
        watchlists = Watchlist.objects.filter(user=user)
        
        results = []
        for watchlist in watchlists:
            watchlist_items = WatchlistItem.objects.filter(watchlist=watchlist)
            
            items = []
            for item in watchlist_items:
                # Her hisse için son fiyat bilgisini al
                stock_info = stock_service.get_stock_info(item.symbol)
                
                if stock_info:
                    items.append({
                        'symbol': item.symbol,
                        'name': stock_info.get('name', ''),
                        'current_price': stock_info.get('current_price'),
                        'change_percent': (stock_info.get('current_price', 0) - stock_info.get('previous_close', 0)) / 
                                         stock_info.get('previous_close', 1) * 100 if stock_info.get('previous_close') else None,
                        'notes': item.notes,
                        'added_at': item.added_at.isoformat()
                    })
            
            results.append({
                'id': watchlist.id,
                'name': watchlist.name,
                'description': watchlist.description,
                'items': items
            })
        
        return Response(results)
    
    except Exception as e:
        logger.error(f"Error in user_watchlist view: {str(e)}")
        return Response(
            {"error": "Failed to fetch user watchlists", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_watchlist(request):
    """
    Kullanıcının izleme listesine hisse ekler
    """
    try:
        user = request.user
        symbol = request.data.get('symbol', '').upper()
        watchlist_id = request.data.get('watchlist_id')
        notes = request.data.get('notes', '')
        
        if not symbol:
            return Response(
                {"error": "Symbol is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sembolün geçerli olup olmadığını kontrol et
        stock_info = stock_service.get_stock_info(symbol)
        if not stock_info:
            return Response(
                {"error": f"Invalid stock symbol: {symbol}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Belirtilen izleme listesini al
        if watchlist_id:
            try:
                watchlist = Watchlist.objects.get(id=watchlist_id, user=user)
            except Watchlist.DoesNotExist:
                return Response(
                    {"error": f"Watchlist with id {watchlist_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # ID belirtilmemişse veya varsayılan izleme listesi yoksa, yeni bir liste oluştur
            default_watchlist, created = Watchlist.objects.get_or_create(
                user=user, 
                name="Default",
                defaults={'description': "My default watchlist"}
            )
            watchlist = default_watchlist
        
        # Hisse daha önce izleme listesine eklenmişse, güncelle
        item, created = WatchlistItem.objects.update_or_create(
            watchlist=watchlist,
            symbol=symbol,
            defaults={'notes': notes}
        )
        
        return Response({
            'status': 'added' if created else 'updated',
            'watchlist_id': watchlist.id,
            'watchlist_name': watchlist.name,
            'symbol': symbol,
            'notes': notes
        })
    
    except Exception as e:
        logger.error(f"Error in add_to_watchlist view: {str(e)}")
        return Response(
            {"error": "Failed to add stock to watchlist", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_watchlist(request):
    """
    Kullanıcının izleme listesinden hisse kaldırır
    """
    try:
        user = request.user
        symbol = request.data.get('symbol', '').upper()
        watchlist_id = request.data.get('watchlist_id')
        
        if not symbol:
            return Response(
                {"error": "Symbol is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not watchlist_id:
            return Response(
                {"error": "Watchlist ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # İzleme listesini kontrol et
        try:
            watchlist = Watchlist.objects.get(id=watchlist_id, user=user)
        except Watchlist.DoesNotExist:
            return Response(
                {"error": f"Watchlist with id {watchlist_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # İzleme listesinden hisseyi kaldır
        deleted, _ = WatchlistItem.objects.filter(watchlist=watchlist, symbol=symbol).delete()
        
        if deleted:
            return Response({
                'status': 'removed',
                'watchlist_id': watchlist.id,
                'watchlist_name': watchlist.name,
                'symbol': symbol
            })
        else:
            return Response(
                {"error": f"Symbol {symbol} not found in watchlist"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    except Exception as e:
        logger.error(f"Error in remove_from_watchlist view: {str(e)}")
        return Response(
            {"error": "Failed to remove stock from watchlist", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
