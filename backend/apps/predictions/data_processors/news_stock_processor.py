# backend/apps/predictions/data_processors/news_stock_processor.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from django.core.cache import caches

from apps.stocks.services.stock_service import StockDataService
from apps.news.services.news_service import NewsService
from apps.news.sentiment.sentiment_analyzer import sentiment_analyzer

logger = logging.getLogger(__name__)

class NewsStockDataProcessor:
    """
    Haber ve hisse senedi verilerini birleştiren ve analiz eden veri işleme sınıfı.
    Bu sınıf, haber duygu skorları ile hisse senedi fiyat hareketleri arasındaki 
    ilişkileri analiz eder ve tahmin modelleri için veri hazırlar.
    """
    
    def __init__(self):
        self.stock_service = StockDataService()
        self.news_service = NewsService()
        self.ml_cache = caches['ml_predictions']
    
    def get_stock_and_news_data(self, symbol, company_name=None, days_back=60):
        """
        Belirli bir hisse senedi için hem fiyat hem de haber verilerini toplar
        """
        try:
            # Önbellekten kontrol et
            cache_key = f"stock_news_data_{symbol}_{days_back}"
            cached_data = self.ml_cache.get(cache_key)
            
            if cached_data:
                logger.info(f"Önbellekten {symbol} için hisse ve haber verileri alınıyor")
                return cached_data
            
            # Hisse bilgilerini al
            stock_info = self.stock_service.get_stock_info(symbol)
            
            # Şirket adı yoksa hisse bilgilerinden al
            if not company_name and stock_info:
                company_name = stock_info.get('name', symbol)
            
            # Tarihsel hisse verileri
            stock_data = self.stock_service.get_historical_data(symbol, period=f"{days_back}d", interval="1d")
            
            # Haber verileri
            news_result = self.news_service.get_stock_specific_news(symbol, days_back=days_back)
            
            # Duygu analizi sonuçları
            sentiment_result = self.news_service.get_sentiment_analysis(symbol, days_back=days_back)
            
            # Sonuçları birleştir
            result = {
                'symbol': symbol,
                'company_name': company_name,
                'stock_info': stock_info,
                'stock_data': stock_data,
                'news_data': news_result.get('articles', []),
                'sentiment_data': sentiment_result.get('sentiment_data', []),
                'average_sentiment': sentiment_result.get('average_sentiment', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Önbelleğe al (4 saat süreyle)
            self.ml_cache.set(cache_key, result, 4 * 3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Hisse ve haber verileri alınırken hata: {str(e)}")
            return None
    
    def analyze_news_with_sentiment(self, news_data):
        """
        Haberleri daha ayrıntılı analiz eder
        """
        try:
            if not news_data or len(news_data) == 0:
                return []
            
            # Gelişmiş duygu analizi ve içerik işleme
            analyzed_news = sentiment_analyzer.analyze_news_batch(news_data)
            
            return analyzed_news
            
        except Exception as e:
            logger.error(f"Haber analizi yapılırken hata: {str(e)}")
            return news_data  # Hata durumunda orijinal veriyi döndür
    
    def merge_stock_and_news_data(self, stock_data, news_data):
        """
        Hisse senedi fiyatları ve haber verilerini tarih bazında birleştirir
        """
        try:
            if not stock_data or not isinstance(stock_data, list) or len(stock_data) == 0:
                logger.error("Geçerli hisse senedi verisi yok")
                return None
                
            # Hisse verilerini DataFrame'e dönüştür
            stock_df = pd.DataFrame(stock_data)
            
            # Tarihleri datetime türüne çevir
            stock_df['date'] = pd.to_datetime(stock_df['date'])
            stock_df.set_index('date', inplace=True)
            
            # Haber yoksa sadece hisse verilerini döndür
            if not news_data or len(news_data) == 0:
                stock_df['sentiment'] = 0
                stock_df['news_count'] = 0
                stock_df['weighted_sentiment'] = 0
                return stock_df
            
            # Duygu analizini uygula
            analyzed_news = self.analyze_news_with_sentiment(news_data)
            
            # Günlük duygu verileri
            daily_sentiment = sentiment_analyzer.generate_daily_sentiment_data(analyzed_news)
            daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])
            daily_sentiment.set_index('date', inplace=True)
            
            # Hisse ve haber verilerini birleştir
            merged_df = stock_df.join(daily_sentiment, how='left')
            
            # Eksik değerleri doldur
            merged_df['sentiment_score'].fillna(0, inplace=True)
            merged_df['importance_score'].fillna(0, inplace=True)
            merged_df['weighted_sentiment'].fillna(0, inplace=True)
            merged_df['news_count'].fillna(0, inplace=True)
            
            # Basitlik için sütun isimlerini standartlaştır
            if 'sentiment_score' in merged_df.columns:
                merged_df['sentiment'] = merged_df['sentiment_score']
            
            # Teknik göstergeleri ekle
            merged_df = self.add_technical_indicators(merged_df)
            
            return merged_df
            
        except Exception as e:
            logger.error(f"Veri birleştirme hatası: {str(e)}")
            return None
    
    def add_technical_indicators(self, df):
        """
        Teknik göstergeleri hesaplar ve DataFrame'e ekler
        """
        try:
            # Kopya oluştur
            result_df = df.copy()
            
            # Eksik sütunları kontrol et ve ekle
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in result_df.columns:
                    logger.warning(f"Teknik göstergeler için gerekli sütun eksik: {col}")
                    return df
            
            # Günlük değişim
            result_df['daily_return'] = result_df['close'].pct_change()
            
            # Hareketli ortalamalar
            result_df['ma5'] = result_df['close'].rolling(window=5).mean()
            result_df['ma10'] = result_df['close'].rolling(window=10).mean()
            result_df['ma20'] = result_df['close'].rolling(window=20).mean()
            
            # Bollinger Bantları
            result_df['ma20_std'] = result_df['close'].rolling(window=20).std()
            result_df['upper_band'] = result_df['ma20'] + 2 * result_df['ma20_std']
            result_df['lower_band'] = result_df['ma20'] - 2 * result_df['ma20_std']
            
            # RSI (Relative Strength Index)
            delta = result_df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            result_df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD (Moving Average Convergence Divergence)
            result_df['ema12'] = result_df['close'].ewm(span=12, adjust=False).mean()
            result_df['ema26'] = result_df['close'].ewm(span=26, adjust=False).mean()
            result_df['macd'] = result_df['ema12'] - result_df['ema26']
            result_df['macd_signal'] = result_df['macd'].ewm(span=9, adjust=False).mean()
            
            # İşlem hacmi değişimleri
            result_df['volume_change'] = result_df['volume'].pct_change()
            result_df['volume_ma5'] = result_df['volume'].rolling(window=5).mean()
            
            # Volatilite (20 günlük standart sapma)
            result_df['volatility'] = result_df['daily_return'].rolling(window=20).std()
            
            # Duygu ve fiyat arasındaki korelasyon (gözlemlenebilir pencere)
            try:
                if 'sentiment' in result_df.columns and len(result_df) >= 5:
                    # 5 günlük kaydırmalı korelasyon
                    result_df['sentiment_price_corr'] = result_df['sentiment'].rolling(window=5).corr(result_df['daily_return'])
            except Exception as e:
                logger.warning(f"Korelasyon hesaplanırken hata: {str(e)}")
                result_df['sentiment_price_corr'] = np.nan
            
            return result_df
            
        except Exception as e:
            logger.error(f"Teknik göstergeler eklenirken hata: {str(e)}")
            return df
    
    def calculate_correlation_metrics(self, merged_df):
        """
        Haber duygu skorları ve hisse senedi fiyatları arasındaki korelasyonları hesaplar
        """
        try:
            if merged_df is None or merged_df.empty:
                return {}
                
            correlations = {}
            
            # Duygu skoru sütun isimlerini kontrol et
            sentiment_columns = ['sentiment', 'sentiment_score', 'weighted_sentiment']
            available_sentiment_columns = [col for col in sentiment_columns if col in merged_df.columns]
            
            if not available_sentiment_columns:
                logger.warning("Duygu skoru sütunu bulunamadı")
                return {}
            
            # Farklı zaman gecikmeleri (lag) için korelasyonları hesapla
            for lag in [0, 1, 2, 3]:
                lag_correlations = {}
                
                for col in available_sentiment_columns:
                    # Duygu skorlarını kaydır
                    if lag > 0:
                        merged_df[f'{col}_lag{lag}'] = merged_df[col].shift(lag)
                        sentiment_col = f'{col}_lag{lag}'
                    else:
                        sentiment_col = col
                    
                    # Günlük değişimle korelasyon
                    if 'daily_return' in merged_df.columns:
                        corr = merged_df[sentiment_col].corr(merged_df['daily_return'])
                        lag_correlations[f'{col}_vs_return'] = corr
                    
                    # Mutlak değişimle korelasyon (volatilite göstergesi)
                    if 'daily_return' in merged_df.columns:
                        abs_return = merged_df['daily_return'].abs()
                        corr = merged_df[sentiment_col].corr(abs_return)
                        lag_correlations[f'{col}_vs_volatility'] = corr
                    
                    # Hacim değişimiyle korelasyon
                    if 'volume_change' in merged_df.columns:
                        corr = merged_df[sentiment_col].corr(merged_df['volume_change'])
                        lag_correlations[f'{col}_vs_volume_change'] = corr
                
                correlations[f'lag_{lag}'] = lag_correlations
            
            # Özet korelasyon metriği hesapla
            best_correlation = 0
            best_lag = 0
            best_metric = ''
            
            for lag, lag_corrs in correlations.items():
                for metric, value in lag_corrs.items():
                    if abs(value) > abs(best_correlation):
                        best_correlation = value
                        best_lag = int(lag.split('_')[1])
                        best_metric = metric
            
            summary = {
                'correlations': correlations,
                'best_correlation': best_correlation,
                'best_lag': best_lag,
                'best_metric': best_metric,
                'correlation_strength': 'strong' if abs(best_correlation) > 0.5 else 'moderate' if abs(best_correlation) > 0.3 else 'weak'
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Korelasyon metrikleri hesaplanırken hata: {str(e)}")
            return {}
    
    def identify_significant_news_dates(self, merged_df, threshold=0.2):
        """
        Hisse senedi fiyatını önemli ölçüde etkilediği düşünülen haber tarihlerini belirler
        """
        try:
            if merged_df is None or merged_df.empty:
                return []
                
            # Duygu skoru sütununu kontrol et
            sentiment_col = None
            for col in ['weighted_sentiment', 'sentiment', 'sentiment_score']:
                if col in merged_df.columns:
                    sentiment_col = col
                    break
            
            if sentiment_col is None or 'daily_return' not in merged_df.columns:
                return []
            
            # Önemli haberleri belirle
            significant_news = []
            
            # İndeksi sıfırla ve tarih sütunu ekle
            df = merged_df.reset_index()
            
            for i in range(1, len(df)):
                # Önemli bir duygu skoru var mı?
                significant_sentiment = abs(df[sentiment_col].iloc[i]) > threshold
                
                # Haber sayısı var mı?
                has_news = df['news_count'].iloc[i] > 0 if 'news_count' in df.columns else True
                
                # Önemli bir fiyat hareketi var mı? (bir önceki güne göre)
                significant_price_move = abs(df['daily_return'].iloc[i]) > 0.01  # %1'den fazla değişim
                
                if significant_sentiment and has_news and significant_price_move:
                    date = df['date'].iloc[i]
                    price_change = df['daily_return'].iloc[i] * 100  # Yüzde olarak
                    sentiment = df[sentiment_col].iloc[i]
                    
                    # Duygu skoru ve fiyat hareketi yönleri uyuşuyor mu?
                    alignment = (sentiment > 0 and price_change > 0) or (sentiment < 0 and price_change < 0)
                    
                    significant_news.append({
                        'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else date,
                        'sentiment': sentiment,
                        'price_change': price_change,
                        'news_count': df['news_count'].iloc[i] if 'news_count' in df.columns else None,
                        'alignment': alignment
                    })
            
            return significant_news
            
        except Exception as e:
            logger.error(f"Önemli haber tarihleri belirlenirken hata: {str(e)}")
            return []
    
    def prepare_prophet_data(self, merged_df, include_regressors=True):
        """
        Facebook Prophet için veri hazırlar
        """
        try:
            if merged_df is None or merged_df.empty or 'close' not in merged_df.columns:
                logger.error("Prophet için geçerli veri yok")
                return None
                
            # Prophet için veri formatı: 'ds' (tarih) ve 'y' (hedef değişken) sütunları
            prophet_df = pd.DataFrame()
            prophet_df['ds'] = merged_df.index
            prophet_df['y'] = merged_df['close']
            
            # Regressor'ları ekle
            if include_regressors:
                # Duygu skoru
                if 'sentiment' in merged_df.columns:
                    prophet_df['sentiment'] = merged_df['sentiment']
                elif 'sentiment_score' in merged_df.columns:
                    prophet_df['sentiment'] = merged_df['sentiment_score']
                
                # Ağırlıklı duygu skoru
                if 'weighted_sentiment' in merged_df.columns:
                    prophet_df['weighted_sentiment'] = merged_df['weighted_sentiment']
                
                # Haber sayısı
                if 'news_count' in merged_df.columns:
                    prophet_df['news_count'] = merged_df['news_count']
                
                # Teknik göstergeler
                technical_indicators = ['rsi', 'macd', 'volatility', 'volume_change']
                for indicator in technical_indicators:
                    if indicator in merged_df.columns:
                        prophet_df[indicator] = merged_df[indicator]
            
            # NaN değerleri doldur
            for col in prophet_df.columns:
                if prophet_df[col].isnull().any():
                    if col == 'ds':
                        continue  # ds sütununu değiştirme
                    elif col == 'y':
                        # Hedef değişkende eksik değer varsa, önceki değeri kullan
                        prophet_df['y'].fillna(method='ffill', inplace=True)
                    else:
                        # Diğer sütunlar için 0 kullan
                        prophet_df[col].fillna(0, inplace=True)
            
            return prophet_df
            
        except Exception as e:
            logger.error(f"Prophet verisi hazırlanırken hata: {str(e)}")
            return None
    
    def get_complete_analysis_data(self, symbol, company_name=None, days_back=60):
        """
        Hisse senedi ve haber verilerini alır, işler ve tam bir analiz seti hazırlar
        """
        try:
            # Veri topla
            data = self.get_stock_and_news_data(symbol, company_name, days_back)
            
            if not data:
                logger.error(f"{symbol} için veri alınamadı")
                return None
            
            # Haberleri analiz et
            if 'news_data' in data and data['news_data']:
                analyzed_news = self.analyze_news_with_sentiment(data['news_data'])
                data['analyzed_news'] = analyzed_news
            else:
                data['analyzed_news'] = []
            
            # Hisse ve haber verilerini birleştir
            merged_df = self.merge_stock_and_news_data(data['stock_data'], data['analyzed_news'])
            data['merged_data'] = merged_df
            
            # Korelasyon metrikleri
            correlation_metrics = self.calculate_correlation_metrics(merged_df)
            data['correlation_metrics'] = correlation_metrics
            
            # Önemli haber tarihleri
            significant_news = self.identify_significant_news_dates(merged_df)
            data['significant_news_dates'] = significant_news
            
            # Prophet için veri
            prophet_data = self.prepare_prophet_data(merged_df)
            data['prophet_data'] = prophet_data
            
            return data
            
        except Exception as e:
            logger.error(f"Tam analiz verileri hazırlanırken hata: {str(e)}")
            return None