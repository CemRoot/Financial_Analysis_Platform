import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)

class MarketDataProcessor:
    """
    Piyasa verilerini işlemek ve özellik çıkarımı yapmak için kullanılan sınıf
    """
    
    def __init__(self):
        self.data_cache = caches['default']
        self.cache_timeout = 3600  # 1 saat
    
    def get_historical_data(self, symbol, period='1y', interval='1d'):
        """
        Hisse senedi için tarihsel fiyat verilerini getirir
        
        Args:
            symbol (str): Hisse sembolü
            period (str): Veri periyodu ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval (str): Veri aralığı ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            list: Hisse senedi verileri listesi [{'date': ..., 'open': ..., 'high': ..., 'low': ..., 'close': ..., 'volume': ...}, ...]
        """
        try:
            # Önbellekte veri var mı kontrol et
            cache_key = f"market_data_{symbol}_{period}_{interval}"
            cached_data = self.data_cache.get(cache_key)
            
            if cached_data:
                logger.info(f"Returning cached market data for {symbol}")
                return cached_data
            
            # Yahoo Finance'ten veri çek
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No data returned for {symbol}")
                return []
            
            # DataFrame'i liste formatına dönüştür
            result = []
            for date, row in hist.iterrows():
                result.append({
                    'date': date.strftime('%Y-%m-%d') if interval == '1d' else date.strftime('%Y-%m-%d %H:%M:%S'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'change': float(row['Close'] / row['Open'] - 1) if not np.isnan(row['Open']) and row['Open'] != 0 else 0,
                })
            
            # Veriyi önbelleğe al
            self.data_cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {str(e)}")
            return []
    
    def get_market_features(self, symbol, period='30d'):
        """
        ML modelleri için piyasa özelliklerini çıkarır
        
        Args:
            symbol (str): Hisse sembolü
            period (str): Veri periyodu
        
        Returns:
            dict: Özellikler ve meta veri içeren sözlük
        """
        try:
            # Önbellekte veri var mı kontrol et
            cache_key = f"market_features_{symbol}_{period}"
            cached_features = self.data_cache.get(cache_key)
            
            if cached_features:
                logger.info(f"Returning cached features for {symbol}")
                return cached_features
            
            # Tarihsel veriyi al
            historical_data = self.get_historical_data(symbol, period=period)
            
            if not historical_data:
                logger.warning(f"No historical data available for {symbol}")
                return None
            
            # DataFrame'e dönüştür
            df = pd.DataFrame(historical_data)
            
            # Tarih sütununu indeks yap
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Teknik indikatörler hesapla
            # 1. Hareketli ortalamalar
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            
            # 2. RSI (Göreceli Güç Endeksi)
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).fillna(0)
            loss = -delta.where(delta < 0, 0).fillna(0)
            
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            
            rs = avg_gain / avg_loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # 3. MACD
            df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = df['ema12'] - df['ema26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            
            # 4. Bollinger Bantları
            df['ma20_std'] = df['close'].rolling(window=20).std()
            df['upper_band'] = df['ma20'] + (df['ma20_std'] * 2)
            df['lower_band'] = df['ma20'] - (df['ma20_std'] * 2)
            
            # 5. Hacim bazlı indikatörler
            df['volume_ma5'] = df['volume'].rolling(window=5).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma5']
            
            # NaN değerleri sil
            df = df.dropna()
            
            if df.empty:
                logger.warning(f"No data left after calculating features for {symbol}")
                return None
            
            # Son satırı al (en güncel veriler)
            latest_row = df.iloc[-1]
            
            # Özellik vektörü oluştur
            features = [
                latest_row['close'],
                latest_row['volume'],
                latest_row['ma5'],
                latest_row['ma10'],
                latest_row['ma20'],
                latest_row['rsi'],
                latest_row['macd'],
                latest_row['macd_signal'],
                latest_row['upper_band'],
                latest_row['lower_band'],
                latest_row['volume_ratio']
            ]
            
            # Son 5 günlük yüzdelik değişim
            if len(df) >= 5:
                features.append(float(df['close'].pct_change(periods=5).iloc[-1]))
            else:
                features.append(0.0)
            
            # Sonuçları sözlük olarak hazırla
            result = {
                'features': features,
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'latest_date': df.index[-1].strftime('%Y-%m-%d'),
                'latest_price': float(latest_row['close'])
            }
            
            # Veriyi önbelleğe al
            self.data_cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting features for {symbol}: {str(e)}")
            return None
    
    def get_market_trend(self, symbol, lookback_days=30):
        """
        Piyasa trendini analiz eder
        
        Args:
            symbol (str): Hisse sembolü
            lookback_days (int): Geriye dönük gün sayısı
        
        Returns:
            dict: Trend analizi sonuçları
        """
        try:
            # Tarihsel veriyi al
            period = f"{lookback_days}d"
            historical_data = self.get_historical_data(symbol, period=period)
            
            if not historical_data or len(historical_data) < 2:
                return {
                    "error": f"Insufficient historical data for {symbol}",
                    "status": "error"
                }
            
            # Veriyi analiz et
            closes = [d['close'] for d in historical_data]
            start_price = closes[0]
            end_price = closes[-1]
            max_price = max(closes)
            min_price = min(closes)
            
            # Yüzdelik değişimler
            overall_change = (end_price / start_price - 1) * 100
            volatility = (max_price - min_price) / start_price * 100
            
            # Trend türünü belirle
            if overall_change > 5:
                trend = "strong_uptrend"
            elif overall_change > 1:
                trend = "uptrend"
            elif overall_change < -5:
                trend = "strong_downtrend"
            elif overall_change < -1:
                trend = "downtrend"
            else:
                trend = "sideways"
            
            # Sonuçları formatlayıp döndür
            return {
                "symbol": symbol,
                "period": f"{lookback_days} days",
                "start_date": historical_data[0]['date'],
                "end_date": historical_data[-1]['date'],
                "start_price": start_price,
                "end_price": end_price,
                "overall_change_percent": overall_change,
                "max_price": max_price,
                "min_price": min_price,
                "volatility_percent": volatility,
                "trend": trend,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market trend for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }
