import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import logging
import random
import pytz
from pandas.tseries.offsets import BDay

logger = logging.getLogger(__name__)

class StockDataService:
    """
    YFinance API'sini kullanarak hisse senedi verilerini çeken servis
    """
    
    @staticmethod
    def is_market_open(symbol='SPY'):
        """
        Determines if the market for a given stock symbol is currently open
        
        The method considers:
        - Regular trading hours (9:30 AM to 4:00 PM Eastern Time)
        - Weekend closures
        - Holiday closures using the most recently available data
        """
        try:
            # Default to US market (SPY ETF) if no symbol provided
            ticker = yf.Ticker(symbol)
            
            # Get basic info about the stock to determine exchange
            info = ticker.info
            exchange = info.get('exchange', '').upper()
            
            # Get timezone based on exchange
            if exchange in ['NYSE', 'NASDAQ']:
                timezone = 'US/Eastern'
            elif exchange == 'LSE':
                timezone = 'Europe/London'
            elif exchange in ['JPX', 'TSE']:
                timezone = 'Asia/Tokyo'
            else:
                # Default to US Eastern for most stocks
                timezone = 'US/Eastern'
            
            # Current time in exchange timezone
            now = datetime.now(pytz.timezone(timezone))
            
            # Check if it's a weekend
            if now.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                return {
                    'is_open': False,
                    'status': 'closed',
                    'reason': 'Weekend',
                    'exchange': exchange,
                    'timezone': timezone,
                    'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'next_open': StockDataService._get_next_business_day(now).strftime('%Y-%m-%d %H:%M:%S %Z')
                }
            
            # Define market hours (using US Eastern as default)
            if timezone == 'US/Eastern':
                market_open = time(9, 30)  # 9:30 AM ET
                market_close = time(16, 0)  # 4:00 PM ET
            elif timezone == 'Europe/London':
                market_open = time(8, 0)   # 8:00 AM London
                market_close = time(16, 30)  # 4:30 PM London
            elif timezone == 'Asia/Tokyo':
                market_open = time(9, 0)   # 9:00 AM Tokyo
                market_close = time(15, 0)  # 3:00 PM Tokyo
            else:
                # Default US hours
                market_open = time(9, 30)
                market_close = time(16, 0)
            
            # Check if current time is within market hours
            current_time = now.time()
            
            # Check for holiday by seeing if there was recent data today
            # (if market should be open but there's no recent data, it's likely a holiday)
            is_holiday = False
            if current_time > market_open and current_time < market_close:
                try:
                    # Get most recent 1-minute data
                    last_data = ticker.history(period="1d", interval="1m")
                    
                    if last_data.empty or (now - last_data.index[-1].to_pydatetime().replace(tzinfo=pytz.timezone(timezone))).total_seconds() > 600:
                        # If last data point is more than 10 minutes old during market hours, likely a holiday
                        is_holiday = True
                except Exception as e:
                    logger.warning(f"Failed to check recent data for holiday detection: {str(e)}")
            
            if is_holiday:
                return {
                    'is_open': False,
                    'status': 'closed',
                    'reason': 'Holiday or Trading Halt',
                    'exchange': exchange,
                    'timezone': timezone,
                    'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'next_open': StockDataService._get_next_business_day(now).strftime('%Y-%m-%d %H:%M:%S %Z')
                }
            
            if market_open <= current_time <= market_close:
                return {
                    'is_open': True,
                    'status': 'open',
                    'exchange': exchange,
                    'timezone': timezone,
                    'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'closing_time': now.replace(hour=market_close.hour, minute=market_close.minute).strftime('%H:%M:%S %Z')
                }
            else:
                # Market is closed during regular hours
                next_open_day = StockDataService._get_next_business_day(now)
                next_open_time = next_open_day.replace(hour=market_open.hour, minute=market_open.minute)
                
                return {
                    'is_open': False,
                    'status': 'closed',
                    'reason': 'Outside trading hours',
                    'exchange': exchange,
                    'timezone': timezone,
                    'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'next_open': next_open_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                }
                
        except Exception as e:
            logger.error(f"Error checking market status: {str(e)}")
            # Provide a reasonable default during errors
            return {
                'is_open': False,
                'status': 'unknown',
                'reason': 'Error determining market status',
                'error': str(e)
            }
    
    @staticmethod
    def _get_next_business_day(current_date):
        """Helper method to get the next business day (excluding weekends)"""
        # Start with tomorrow
        next_day = current_date + timedelta(days=1)
        
        # If it's a weekend, move to Monday
        if next_day.weekday() >= 5:  # Saturday or Sunday
            days_to_add = 7 - next_day.weekday()
            next_day = current_date + timedelta(days=days_to_add)
            
        return next_day
    
    @staticmethod
    def get_stock_info(symbol):
        """
        Bir hisse senedi hakkında temel bilgileri al
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get market status
            market_status = StockDataService.is_market_open(symbol)
            
            # Gerekli alanları içeren temiz bir sözlük döndür
            result = {
                'symbol': symbol,
                'name': info.get('shortName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', None),
                'current_price': info.get('currentPrice', None),
                'previous_close': info.get('previousClose', None),
                'open': info.get('open', None),
                'day_high': info.get('dayHigh', None),
                'day_low': info.get('dayLow', None),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', None),
                'volume': info.get('volume', None),
                'average_volume': info.get('averageVolume', None),
                'pe_ratio': info.get('trailingPE', None),
                'eps': info.get('trailingEps', None),
                'dividend_yield': info.get('dividendYield', None) * 100 if info.get('dividendYield') else None,
                'beta': info.get('beta', None),
                'website': info.get('website', ''),
                'logo_url': info.get('logo_url', ''),
                'market_status': market_status
            }
            
            # If price is missing, try to get it from recent history
            if result['current_price'] is None:
                try:
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        result['current_price'] = round(float(hist['Close'].iloc[-1]), 2)
                except Exception as e:
                    logger.warning(f"Could not retrieve current price from history for {symbol}: {str(e)}")
            
            # Calculate price change and percentage
            if result['current_price'] and result['previous_close']:
                result['price_change'] = round(result['current_price'] - result['previous_close'], 2)
                result['change_percent'] = round((result['price_change'] / result['previous_close']) * 100, 2)
            
            return result
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
            # Return fallback data instead of None
            return StockDataService._generate_fallback_stock_info(symbol)
    
    @staticmethod
    def _generate_fallback_stock_info(symbol):
        """
        Generate fallback stock information when the API fails
        """
        logger.info(f"Generating fallback stock info for {symbol}")
        
        # Map common stock symbols to company names for better fallback data
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
            'BAC': 'Bank of America Corporation',
            'DIS': 'The Walt Disney Company',
            'NFLX': 'Netflix Inc.',
            'CSCO': 'Cisco Systems Inc.',
            'INTC': 'Intel Corporation',
            'XOM': 'Exxon Mobil Corporation',
            'KO': 'The Coca-Cola Company',
            'PEP': 'PepsiCo Inc.',
            'WMT': 'Walmart Inc.',
            'PG': 'Procter & Gamble Co.',
            'JNJ': 'Johnson & Johnson'
        }
        
        # Generate realistic base price based on the symbol
        base_price = 0
        for char in symbol:
            base_price += ord(char)
        base_price = (base_price % 900) + 100  # Price between $100 and $1000
        
        # Add small random variation
        current_price = round(base_price * (1 + (random.random() - 0.5) * 0.02), 2)
        previous_close = round(current_price * (1 + (random.random() - 0.5) * 0.01), 2)
        day_open = round(previous_close * (1 + (random.random() - 0.5) * 0.005), 2)
        day_high = round(max(current_price, day_open) * (1 + random.random() * 0.01), 2)
        day_low = round(min(current_price, day_open) * (1 - random.random() * 0.01), 2)
        
        # Determine sector based on first letter
        sectors = ['Technology', 'Healthcare', 'Consumer Cyclical', 'Financial Services', 
                  'Communication Services', 'Industrials', 'Energy', 'Consumer Defensive', 
                  'Utilities', 'Real Estate', 'Basic Materials']
        sector_index = ord(symbol[0]) % len(sectors)
        sector = sectors[sector_index]
        
        # Choose industry based on sector
        industries = {
            'Technology': ['Software—Application', 'Semiconductors', 'Consumer Electronics', 'Software—Infrastructure'],
            'Healthcare': ['Biotechnology', 'Drug Manufacturers—General', 'Medical Devices', 'Healthcare Plans'],
            'Consumer Cyclical': ['Auto Manufacturers', 'Specialty Retail', 'Restaurants', 'Apparel Retail'],
            'Financial Services': ['Banks—Diversified', 'Capital Markets', 'Insurance—Diversified', 'Credit Services'],
            'Communication Services': ['Internet Content & Information', 'Entertainment', 'Telecom Services', 'Advertising Agencies'],
            'Industrials': ['Aerospace & Defense', 'Farm & Heavy Construction Machinery', 'Airlines', 'Integrated Freight & Logistics'],
            'Energy': ['Oil & Gas E&P', 'Oil & Gas Integrated', 'Oil & Gas Midstream', 'Oil & Gas Equipment & Services'],
            'Consumer Defensive': ['Beverages—Non-Alcoholic', 'Packaged Foods', 'Discount Stores', 'Household & Personal Products'],
            'Utilities': ['Utilities—Regulated Electric', 'Utilities—Regulated Gas', 'Utilities—Renewable', 'Utilities—Diversified'],
            'Real Estate': ['REIT—Diversified', 'REIT—Office', 'REIT—Residential', 'Real Estate Services'],
            'Basic Materials': ['Chemicals', 'Steel', 'Agricultural Inputs', 'Gold']
        }
        industry = random.choice(industries.get(sector, ['Diversified']))
        
        return {
            'symbol': symbol,
            'name': stock_names.get(symbol, f"{symbol} Corporation"),
            'sector': sector,
            'industry': industry,
            'market_cap': round(base_price * 1000000000 * (1 + random.random()), 2),
            'current_price': current_price,
            'previous_close': previous_close,
            'open': day_open,
            'day_high': day_high,
            'day_low': day_low,
            'fifty_two_week_high': round(current_price * 1.25, 2),
            'fifty_two_week_low': round(current_price * 0.75, 2),
            'volume': int(random.random() * 10000000) + 1000000,
            'average_volume': int(random.random() * 8000000) + 2000000,
            'pe_ratio': round(random.random() * 30 + 10, 2),
            'eps': round(current_price / (random.random() * 20 + 10), 2),
            'dividend_yield': round(random.random() * 3, 2),
            'beta': round(0.5 + random.random() * 1.5, 2),
            'website': f"https://www.{symbol.lower()}.com",
            'logo_url': f"https://logo.clearbit.com/{symbol.lower()}.com",
            'is_fallback': True  # Indicate this is fallback data
        }
    
    @staticmethod
    def get_historical_data(symbol, period='1y', interval='1d'):
        """
        Bir hisse senedi için tarihsel veriler al
        
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        logger.info(f"StockDataService: Getting historical data for {symbol} with period={period}, interval={interval}")
        
        try:
            logger.info(f"Creating YFinance ticker for {symbol}")
            stock = yf.Ticker(symbol)
            
            logger.info(f"Fetching history for {symbol}")
            hist = stock.history(period=period, interval=interval)
            
            logger.info(f"Retrieved data shape: {hist.shape}, empty: {hist.empty}")
            
            # DataFrame'i işle ve döndür
            if not hist.empty:
                hist.reset_index(inplace=True)
                
                # Debug column names
                logger.info(f"History columns: {hist.columns.tolist()}")
                
                # Eğer 'Datetime' sütunu varsa, onu datetime nesnesine dönüştür
                if 'Datetime' in hist.columns:
                    hist['Date'] = hist['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif 'Date' in hist.columns:
                    hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
                
                # Temiz bir sözlük listesi döndür
                result = []
                for _, row in hist.iterrows():
                    result.append({
                        'date': row.get('Date'),
                        'open': float(row.get('Open')) if not pd.isna(row.get('Open')) else None,
                        'high': float(row.get('High')) if not pd.isna(row.get('High')) else None,
                        'low': float(row.get('Low')) if not pd.isna(row.get('Low')) else None,
                        'close': float(row.get('Close')) if not pd.isna(row.get('Close')) else None,
                        'volume': int(row.get('Volume')) if not pd.isna(row.get('Volume')) else 0,
                    })
                
                if result:
                    logger.info(f"Successfully processed {len(result)} data points for {symbol}")
                    return result
                
                # If we got an empty result, generate fallback data
                logger.warning(f"Empty historical data for {symbol}, using fallback")
                return StockDataService._generate_fallback_historical_data(symbol, period, interval)
            
            # Empty DataFrame, generate fallback data
            logger.warning(f"Empty historical data for {symbol}, using fallback")
            return StockDataService._generate_fallback_historical_data(symbol, period, interval)
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}", exc_info=True)
            # Return fallback data instead of empty list
            return StockDataService._generate_fallback_historical_data(symbol, period, interval)
    
    @staticmethod
    def _generate_fallback_historical_data(symbol, period='1y', interval='1d'):
        """
        Generate fallback historical data when the API fails
        """
        logger.info(f"Generating fallback historical data for {symbol} with period={period}, interval={interval}")
        
        # Determine the date range based on the period
        end_date = datetime.now()
        period_map = {
            '1d': timedelta(days=1),
            '5d': timedelta(days=5),
            '1mo': timedelta(days=30),
            '3mo': timedelta(days=90),
            '6mo': timedelta(days=180),
            '1y': timedelta(days=365),
            '2y': timedelta(days=365*2),
            '5y': timedelta(days=365*5),
            '10y': timedelta(days=365*10),
            'ytd': timedelta(days=(end_date - datetime(end_date.year, 1, 1)).days),
            'max': timedelta(days=365*10)  # Use 10 years for 'max'
        }
        time_delta = period_map.get(period, timedelta(days=365))  # Default to 1 year
        start_date = end_date - time_delta
        
        # Determine the interval between data points
        interval_map = {
            '1m': timedelta(minutes=1),
            '2m': timedelta(minutes=2),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '30m': timedelta(minutes=30),
            '60m': timedelta(hours=1),
            '90m': timedelta(minutes=90),
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1),
            '5d': timedelta(days=5),
            '1wk': timedelta(weeks=1),
            '1mo': timedelta(days=30),
            '3mo': timedelta(days=90)
        }
        interval_delta = interval_map.get(interval, timedelta(days=1))  # Default to 1 day
        
        # Generate base price and volatility based on symbol
        base_price = 0
        for char in symbol:
            base_price += ord(char)
        base_price = (base_price % 900) + 100  # Between $100 and $1000
        volatility = (ord(symbol[0]) % 5 + 1) / 100  # Between 1% and 5%
        
        # Generate data points
        result = []
        current_date = start_date
        current_price = base_price
        
        # Realistic price movement with long-term trend
        trend = (random.random() - 0.4) * 0.001  # Slight bullish bias
        
        while current_date <= end_date:
            # Skip weekends if using daily or longer intervals
            if interval_delta >= timedelta(days=1):
                if current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                    current_date += timedelta(days=1)
                    continue
            
            # Random price movement with some momentum
            daily_change = np.random.normal(trend, volatility)
            open_price = current_price
            close_price = open_price * (1 + daily_change)
            
            # High and low prices
            daily_volatility = volatility * open_price
            high_price = max(open_price, close_price) + abs(np.random.normal(0, daily_volatility))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, daily_volatility))
            
            # Random but realistic volume
            volume = int(np.random.normal(5000000, 2000000))
            volume = max(100000, volume)  # Ensure positive volume
            
            # Format date based on interval
            date_format = '%Y-%m-%d %H:%M:%S' if interval_delta < timedelta(days=1) else '%Y-%m-%d'
            
            result.append({
                'date': current_date.strftime(date_format),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
            
            # Update for next iteration
            current_price = close_price
            current_date += interval_delta
        
        # Add fallback indicator
        for item in result:
            item['is_fallback'] = True
            
        return result
    
    @staticmethod
    def get_market_movers():
        """
        Piyasadaki en çok yükselen ve düşen hisseleri al
        """
        try:
            # S&P 500 sembollerini al
            sp500 = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'NVDA', 'JPM', 'V']
            
            # Son fiyatları al
            data = []
            for symbol in sp500[:10]:  # İlk 10 sembolü al (hızlı olması için)
                stock = yf.Ticker(symbol)
                info = stock.info
                hist = stock.history(period="2d")
                
                if len(hist) >= 2:
                    prev_close = hist.iloc[-2]['Close']
                    current_close = hist.iloc[-1]['Close']
                    change = (current_close - prev_close) / prev_close * 100
                    
                    data.append({
                        'symbol': symbol,
                        'name': info.get('shortName', symbol),
                        'current_price': current_close,
                        'change_percent': change,
                        'volume': hist.iloc[-1]['Volume'],
                    })
            
            # If we have data, return it
            if len(data) >= 5:
                # Değişim yüzdesine göre sırala
                gainers = sorted(data, key=lambda x: x['change_percent'], reverse=True)[:5]
                losers = sorted(data, key=lambda x: x['change_percent'])[:5]
                
                return {
                    'gainers': gainers,
                    'losers': losers
                }
            
            # If we don't have enough data, generate fallback data
            logger.warning("Not enough market movers data, using fallback")
            return StockDataService._generate_fallback_market_movers()
            
        except Exception as e:
            logger.error(f"Error fetching market movers: {str(e)}")
            # Return fallback data instead of empty lists
            return StockDataService._generate_fallback_market_movers()
    
    @staticmethod
    def _generate_fallback_market_movers():
        """
        Generate fallback market movers data when the API fails
        """
        logger.info("Generating fallback market movers data")
        
        # Common stock symbols and names
        stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
            {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.'},
            {'symbol': 'V', 'name': 'Visa Inc.'},
            {'symbol': 'BAC', 'name': 'Bank of America Corporation'},
            {'symbol': 'DIS', 'name': 'The Walt Disney Company'},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
            {'symbol': 'CSCO', 'name': 'Cisco Systems Inc.'},
            {'symbol': 'INTC', 'name': 'Intel Corporation'},
            {'symbol': 'XOM', 'name': 'Exxon Mobil Corporation'}
        ]
        
        # Generate realistic but random data for each stock
        all_movers = []
        for stock in stocks:
            base_price = 0
            for char in stock['symbol']:
                base_price += ord(char)
            base_price = (base_price % 900) + 100  # Between $100 and $1000
            
            change_percent = np.random.normal(0, 3)  # Normal distribution with 3% std dev
            
            all_movers.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'current_price': round(base_price, 2),
                'change_percent': round(change_percent, 2),
                'volume': int(np.random.normal(5000000, 2000000)),
                'is_fallback': True
            })
        
        # Sort to get gainers and losers
        gainers = sorted(all_movers, key=lambda x: x['change_percent'], reverse=True)[:5]
        losers = sorted(all_movers, key=lambda x: x['change_percent'])[:5]
        
        return {
            'gainers': gainers,
            'losers': losers,
            'is_fallback': True
        }