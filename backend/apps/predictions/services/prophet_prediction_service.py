# backend/apps/predictions/services/prophet_prediction_service.py

import logging
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from django.conf import settings
from django.core.cache import caches

from ..data_processors.news_stock_processor import NewsStockDataProcessor
from ..ml_models.prophet_models import StockProphetModel, NewsEnhancedProphetModel
from apps.news.services.news_service import NewsService
from apps.stocks.services.stock_service import StockDataService

logger = logging.getLogger(__name__)

class ProphetPredictionService:
    """
    Facebook Prophet modelini kullanarak haber duyarlılık analizi ve hisse senedi tahminleri yapar
    """
    
    def __init__(self):
        self.data_processor = NewsStockDataProcessor()
        self.stock_service = StockDataService()
        self.news_service = NewsService()
        self.ml_models_dir = settings.ML_MODELS_DIR
        self.ml_cache = caches['ml_predictions']
    
    def predict_with_prophet(self, symbol, forecast_days=30, include_news=True):
        """
        Prophet modeli ile hisse senedi fiyat tahmini yapar
        """
        try:
            # Önbelleği kontrol et
            cache_key = f"prophet_prediction_{symbol}_{forecast_days}_{include_news}"
            cached_prediction = self.ml_cache.get(cache_key)
            
            if cached_prediction:
                logger.info(f"Önbellekten {symbol} için Prophet tahmini alınıyor")
                return cached_prediction
            
            # Tam analiz verilerini al
            data = self.data_processor.get_complete_analysis_data(symbol, days_back=max(60, forecast_days*2))
            
            if not data or 'prophet_data' not in data or data['prophet_data'] is None:
                logger.error(f"{symbol} için Prophet verisi hazırlanamadı")
                return self._generate_fallback_prophet_prediction(symbol, forecast_days)
            
            # Prophet modeli oluştur
            if include_news and 'sentiment' in data['prophet_data'].columns:
                # Haber duyarlılığı içeren zenginleştirilmiş model
                logger.info(f"{symbol} için haber duyarlılığı içeren Prophet modeli oluşturuluyor")
                model = NewsEnhancedProphetModel()
                prophet_df = data['prophet_data']
                
                # Modeli oluştur ve eğit
                model.build_enhanced_model(
                    changepoint_prior_scale=0.05,
                    seasonality_prior_scale=10.0,
                    seasonality_mode='multiplicative',
                    daily_seasonality=False,
                    weekly_seasonality=True,
                    yearly_seasonality=True
                )
                
                model.fit(prophet_df)
                
                # Duygu skorları ile tahmin yap
                if 'sentiment' in prophet_df.columns:
                    # Son 7 günün ortalama duygu skorunu kullan
                    recent_sentiment = prophet_df['sentiment'].iloc[-7:].mean() if len(prophet_df) >= 7 else prophet_df['sentiment'].mean()
                    
                    # Tahmin yap
                    forecast = model.predict_with_future_sentiment(periods=forecast_days, future_sentiment=recent_sentiment)
                else:
                    # Temel tahmin yap
                    forecast = model.predict(periods=forecast_days)
            else:
                # Yalnızca teknik veriler içeren basit model
                logger.info(f"{symbol} için temel Prophet modeli oluşturuluyor")
                model = StockProphetModel()
                prophet_df = data['prophet_data'][['ds', 'y']]
                
                # Modeli oluştur ve eğit
                model.build_model()
                model.fit(prophet_df)
                
                # Tahmin yap
                forecast = model.predict(periods=forecast_days)
            
            # Sonuçları formatla
            result = model.format_results(symbol, forecast_days)
            
            # Grafiği oluştur ve veri olarak dönüştür
            try:
                # İnteraktif grafik oluştur
                fig = model.create_interactive_plot(symbol, include_sentiment=include_news)
                
                if fig:
                    # Grafiği JSON olarak kaydet
                    result['interactive_plot'] = fig.to_json()
            except Exception as plot_err:
                logger.error(f"Grafik oluşturulurken hata: {str(plot_err)}")
            
            # Ek analiz bilgilerini ekle
            result['news_enhanced'] = include_news
            result['analysis_summary'] = self._create_analysis_summary(data, result)
            
            # Sonucu önbelleğe al (4 saat süreyle)
            self.ml_cache.set(cache_key, result, 4 * 3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Prophet tahmini yapılırken hata: {str(e)}")
            return self._generate_fallback_prophet_prediction(symbol, forecast_days)
    
    def _create_analysis_summary(self, data, forecast_result):
        """
        Analiz verilerini ve tahmin sonuçlarını kullanarak özet bir analiz oluşturur
        """
        try:
            summary = {}
            
            # Haber duyarlılığı özeti
            if 'average_sentiment' in data:
                summary['news_sentiment'] = {
                    'average_sentiment': data['average_sentiment'],
                    'sentiment_category': 'positive' if data['average_sentiment'] > 0.2 else 'negative' if data['average_sentiment'] < -0.2 else 'neutral'
                }
            
            # Korelasyon metrikleri
            if 'correlation_metrics' in data and data['correlation_metrics']:
                summary['correlation'] = {
                    'best_correlation': data['correlation_metrics'].get('best_correlation', 0),
                    'best_lag': data['correlation_metrics'].get('best_lag', 0),
                    'correlation_strength': data['correlation_metrics'].get('correlation_strength', 'weak')
                }
            
            # Önemli haberler
            if 'significant_news_dates' in data and data['significant_news_dates']:
                # Son 7 gündeki önemli haberleri al
                recent_significant = []
                seven_days_ago = datetime.now() - timedelta(days=7)
                
                for news in data['significant_news_dates']:
                    try:
                        news_date = datetime.strptime(news['date'], '%Y-%m-%d')
                        if news_date >= seven_days_ago:
                            recent_significant.append(news)
                    except (ValueError, TypeError):
                        continue
                
                summary['recent_significant_news'] = recent_significant[:3]  # En fazla 3 tane
                
                # Duygu-fiyat uyumu analizi
                aligned_count = sum(1 for news in data['significant_news_dates'] if news.get('alignment', False))
                total_count = len(data['significant_news_dates'])
                
                if total_count > 0:
                    summary['sentiment_price_alignment'] = {
                        'alignment_ratio': aligned_count / total_count,
                        'alignment_strength': 'strong' if aligned_count / total_count > 0.7 else 'moderate' if aligned_count / total_count > 0.5 else 'weak'
                    }
            
            # Tahmin güvenilirliği
            if 'uncertainty_range' in forecast_result and 'forecasted_price' in forecast_result:
                uncertainty_percent = (forecast_result['uncertainty_range'] / forecast_result['forecasted_price']) * 100
                
                summary['forecast_confidence'] = {
                    'uncertainty_range_percent': float(uncertainty_percent),
                    'confidence_level': 'high' if uncertainty_percent < 5 else 'medium' if uncertainty_percent < 10 else 'low'
                }
            
            # Teknik göstergeler ve trend analizi
            if 'merged_data' in data and not data['merged_data'].empty:
                df = data['merged_data']
                
                # Son değerleri al
                last_row = df.iloc[-1]
                
                # RSI analizi
                if 'rsi' in last_row:
                    rsi = last_row['rsi']
                    rsi_signal = 'overbought' if rsi > 70 else 'oversold' if rsi < 30 else 'neutral'
                    
                    summary['technical_indicators'] = {
                        'rsi': float(rsi),
                        'rsi_signal': rsi_signal
                    }
                
                # MACD analizi
                if 'macd' in last_row and 'macd_signal' in last_row:
                    macd = last_row['macd']
                    macd_signal = last_row['macd_signal']
                    macd_hist = macd - macd_signal
                    
                    if 'technical_indicators' not in summary:
                        summary['technical_indicators'] = {}
                        
                    summary['technical_indicators'].update({
                        'macd': float(macd),
                        'macd_signal': float(macd_signal),
                        'macd_histogram': float(macd_hist),
                        'macd_signal_type': 'bullish' if macd_hist > 0 else 'bearish'
                    })
                
                # Trend analizi
                if 'ma20' in last_row and 'ma5' in last_row:
                    price = last_row['close']
                    ma5 = last_row['ma5']
                    ma20 = last_row['ma20']
                    
                    if 'technical_indicators' not in summary:
                        summary['technical_indicators'] = {}
                        
                    summary['technical_indicators'].update({
                        'trend': 'strong_uptrend' if price > ma5 > ma20 else
                                'uptrend' if price > ma20 else
                                'strong_downtrend' if price < ma5 < ma20 else
                                'downtrend' if price < ma20 else
                                'neutral'
                    })
            
            # Özet tahmin mesajı
            try:
                percent_change = forecast_result.get('percent_change', 0)
                forecast_direction = 'increase' if percent_change > 0 else 'decrease' if percent_change < 0 else 'remain stable'
                
                confidence = summary.get('forecast_confidence', {}).get('confidence_level', 'medium')
                sentiment_category = summary.get('news_sentiment', {}).get('sentiment_category', 'neutral')
                
                tech_indicators = summary.get('technical_indicators', {})
                trend = tech_indicators.get('trend', 'neutral')
                rsi_signal = tech_indicators.get('rsi_signal', 'neutral')
                
                # Özet mesaj oluştur
                message = f"The {symbol} stock price is forecasted to {forecast_direction} by {abs(percent_change):.2f}% over the next {forecast_result.get('forecast_days', 30)} days. "
                
                message += f"This forecast has {confidence} confidence. "
                
                if sentiment_category != 'neutral':
                    message += f"Recent news sentiment is {sentiment_category}. "
                
                if trend != 'neutral':
                    trend_msg = trend.replace('_', ' ')
                    message += f"Technical analysis shows a {trend_msg}. "
                
                if rsi_signal != 'neutral':
                    message += f"RSI indicates the stock is currently {rsi_signal}. "
                
                summary['forecast_message'] = message
                
            except Exception as msg_err:
                logger.error(f"Özet mesaj oluşturulurken hata: {str(msg_err)}")
                summary['forecast_message'] = f"The {symbol} stock price is forecasted to change by {forecast_result.get('percent_change', 0):.2f}% over the next {forecast_result.get('forecast_days', 30)} days."
            
            return summary
            
        except Exception as e:
            logger.error(f"Analiz özeti oluşturulurken hata: {str(e)}")
            return {}
    
    def _generate_fallback_prophet_prediction(self, symbol, forecast_days=30):
        """
        Gerçek tahmin yapılamadığında fallback veri oluşturur
        """
        logger.info(f"{symbol} için fallback Prophet tahmini oluşturuluyor")
        
        try:
            # Temel hisse bilgilerini al
            stock_info = self.stock_service.get_stock_info(symbol)
            
            if not stock_info:
                return {
                    "error": f"Failed to get stock information for {symbol}",
                    "status": "error"
                }
            
            current_price = stock_info.get('current_price')
            
            if not current_price:
                current_price = 100.0  # Varsayılan değer
            
            # Rastgele ama gerçekçi bir trend oluştur
            trend_percent = np.random.normal(0, 2.0)  # %2 standart sapma
            end_price = current_price * (1 + trend_percent / 100)
            
            # Günlük tahminler oluştur
            daily_forecasts = []
            today = datetime.now()
            
            volatility = 0.5  # Günlük volatilite (%)
            
            for i in range(1, forecast_days + 1):
                # Linear interpolation between current and end price
                ratio = i / forecast_days
                predicted_price = current_price * (1 - ratio) + end_price * ratio
                
                # Add small random noise
                daily_volatility = np.random.normal(0, volatility)
                predicted_price = predicted_price * (1 + daily_volatility / 100)
                
                forecast_date = today + timedelta(days=i)
                
                lower_bound = predicted_price * 0.98  # %2 alt sınır
                upper_bound = predicted_price * 1.02  # %2 üst sınır
                
                daily_forecasts.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'price': float(predicted_price),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound)
                })
            
            # Son değeri al
            last_forecast = daily_forecasts[-1]['price']
            
            result = {
                'symbol': symbol,
                'current_price': float(current_price),
                'forecast_end_date': daily_forecasts[-1]['date'],
                'forecasted_price': float(last_forecast),
                'price_change': float(last_forecast - current_price),
                'percent_change': float(trend_percent),
                'confidence_interval': {
                    'lower': float(daily_forecasts[-1]['lower_bound']),
                    'upper': float(daily_forecasts[-1]['upper_bound'])
                },
                'uncertainty_range': float(daily_forecasts[-1]['upper_bound'] - daily_forecasts[-1]['lower_bound']),
                'forecast_days': forecast_days,
                'daily_forecasts': daily_forecasts,
                'news_enhanced': False,
                'is_fallback': True,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'analysis_summary': {
                    'forecast_message': f"The {symbol} stock price is forecasted to change by {trend_percent:.2f}% over the next {forecast_days} days. This is a fallback prediction as the actual model could not be computed."
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Fallback tahmin oluşturulurken hata: {str(e)}")
            return {
                "error": f"Failed to generate prediction for {symbol}: {str(e)}",
                "status": "error"
            }
    
    def analyze_news_impact(self, symbol, days_back=30):
        """
        Haberlerin hisse senedi fiyatı üzerindeki etkisini analiz eder
        """
        try:
            # Önbelleği kontrol et
            cache_key = f"news_impact_{symbol}_{days_back}"
            cached_analysis = self.ml_cache.get(cache_key)
            
            if cached_analysis:
                logger.info(f"Önbellekten {symbol} için haber etkisi analizi alınıyor")
                return cached_analysis
            
            # Veri al
            data = self.data_processor.get_complete_analysis_data(symbol, days_back=days_back)
            
            if not data:
                logger.error(f"{symbol} için veri alınamadı")
                return {
                    "error": f"Failed to get data for {symbol}",
                    "status": "error"
                }
            
            # Korelasyon metrikleri
            correlation_metrics = data.get('correlation_metrics', {})
            
            # Önemli haber tarihleri
            significant_news = data.get('significant_news_dates', [])
            
            # Duygu dağılımı
            sentiment_distribution = {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            }
            
            if 'analyzed_news' in data and data['analyzed_news']:
                for news in data['analyzed_news']:
                    sentiment = news.get('sentiment_score', 0)
                    if sentiment > 0.2:
                        sentiment_distribution['positive'] += 1
                    elif sentiment < -0.2:
                        sentiment_distribution['negative'] += 1
                    else:
                        sentiment_distribution['neutral'] += 1
                
                # Yüzdelere dönüştür
                total_news = len(data['analyzed_news'])
                if total_news > 0:
                    for key in sentiment_distribution:
                        sentiment_distribution[key] = (sentiment_distribution[key] / total_news) * 100
            
            # Analizin özet sonuçları
            result = {
                'symbol': symbol,
                'days_analyzed': days_back,
                'total_news_count': len(data.get('analyzed_news', [])),
                'significant_news_count': len(significant_news),
                'average_sentiment': data.get('average_sentiment', 0),
                'sentiment_distribution': sentiment_distribution,
                'correlation_metrics': correlation_metrics,
                'significant_news': significant_news,
                'impact_analysis': self._analyze_news_impact_patterns(data),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            # Sonucu önbelleğe al (6 saat süreyle)
            self.ml_cache.set(cache_key, result, 6 * 3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Haber etkisi analizi yapılırken hata: {str(e)}")
            return {
                "error": f"Failed to analyze news impact for {symbol}: {str(e)}",
                "status": "error"
            }
    
    def _analyze_news_impact_patterns(self, data):
        """
        Haber duyarlılığı ve fiyat hareketleri arasındaki örüntüleri analiz eder
        """
        try:
            if not data or 'merged_data' not in data or data['merged_data'] is None or data['merged_data'].empty:
                return {}
            
            df = data['merged_data']
            
            # Duygu skorunu kontrol et
            sentiment_col = None
            for col in ['sentiment', 'sentiment_score', 'weighted_sentiment']:
                if col in df.columns:
                    sentiment_col = col
                    break
            
            if sentiment_col is None or 'daily_return' not in df.columns:
                return {}
            
            # Duygu ve getiri arasındaki uyum sayısını hesapla
            df['aligned'] = ((df[sentiment_col] > 0) & (df['daily_return'] > 0)) | ((df[sentiment_col] < 0) & (df['daily_return'] < 0))
            
            # Duygu kategorileri
            df['sentiment_category'] = 'neutral'
            df.loc[df[sentiment_col] > 0.2, 'sentiment_category'] = 'positive'
            df.loc[df[sentiment_col] < -0.2, 'sentiment_category'] = 'negative'
            
            # Haber olan günleri filtrele
            if 'news_count' in df.columns:
                news_days = df[df['news_count'] > 0]
            else:
                news_days = df[df[sentiment_col] != 0]
            
            if news_days.empty:
                return {}
            
            # Uyum oranı
            alignment_ratio = news_days['aligned'].mean() if len(news_days) > 0 else 0
            
            # Duygu kategorilerine göre getiri ortalamaları
            returns_by_sentiment = {}
            for category in ['positive', 'neutral', 'negative']:
                category_returns = df[df['sentiment_category'] == category]['daily_return']
                if not category_returns.empty:
                    returns_by_sentiment[category] = {
                        'mean_return': float(category_returns.mean() * 100),  # Yüzde olarak
                        'count': int(len(category_returns))
                    }
                else:
                    returns_by_sentiment[category] = {
                        'mean_return': 0,
                        'count': 0
                    }
            
            # Duygu sonrası fiyat etkisi (lag analizi)
            lagged_effects = {}
            for lag in [1, 2, 3]:
                df[f'lagged_return_{lag}'] = df['daily_return'].shift(-lag)  # Negatif shift: gelecek değerleri
                
                lagged_correlations = {}
                for category in ['positive', 'neutral', 'negative']:
                    category_data = df[df['sentiment_category'] == category]
                    if not category_data.empty and len(category_data) > lag:
                        corr = category_data[sentiment_col].corr(category_data[f'lagged_return_{lag}'])
                        mean_future_return = category_data[f'lagged_return_{lag}'].mean() * 100  # Yüzde olarak
                        lagged_correlations[category] = {
                            'correlation': float(corr) if not pd.isna(corr) else 0,
                            'mean_future_return': float(mean_future_return) if not pd.isna(mean_future_return) else 0
                        }
                
                lagged_effects[f'lag_{lag}'] = lagged_correlations
            
            # Gelecekteki fiyat hareketleriyle en güçlü korelasyona sahip gecikme
            best_lag = 1
            best_corr = 0
            for lag in [1, 2, 3]:
                for category in ['positive', 'negative']:
                    if abs(lagged_effects[f'lag_{lag}'][category]['correlation']) > abs(best_corr):
                        best_corr = lagged_effects[f'lag_{lag}'][category]['correlation']
                        best_lag = lag
            
            # En yüksek getiri farkı olan gecikme
            max_return_diff = 0
            max_diff_lag = 1
            for lag in [1, 2, 3]:
                pos_return = lagged_effects[f'lag_{lag}']['positive']['mean_future_return']
                neg_return = lagged_effects[f'lag_{lag}']['negative']['mean_future_return']
                diff = abs(pos_return - neg_return)
                if diff > max_return_diff:
                    max_return_diff = diff
                    max_diff_lag = lag
            
            # Duygu etkisi örüntüleri
            patterns = {
                'alignment_ratio': float(alignment_ratio),
                'returns_by_sentiment': returns_by_sentiment,
                'lagged_effects': lagged_effects,
                'best_predictive_lag': {
                    'lag': best_lag,
                    'correlation': best_corr
                },
                'max_return_difference': {
                    'lag': max_diff_lag,
                    'difference': max_return_diff
                }
            }
            
            # Özet bulguları ekle
            patterns['findings'] = []
            
            # Uyum oranı yorumu
            if alignment_ratio > 0.7:
                patterns['findings'].append("News sentiment and price movements are strongly aligned, suggesting high market efficiency for this stock.")
            elif alignment_ratio > 0.5:
                patterns['findings'].append("News sentiment and price movements show moderate alignment.")
            else:
                patterns['findings'].append("News sentiment and price movements often diverge, indicating other factors may be more influential.")
            
            # Duygu-getiri ilişkisi yorumu
            pos_ret = returns_by_sentiment['positive']['mean_return']
            neg_ret = returns_by_sentiment['negative']['mean_return']
            if pos_ret > 0.5 and neg_ret < -0.5:
                patterns['findings'].append(f"Positive news typically results in {pos_ret:.2f}% returns, while negative news leads to {neg_ret:.2f}% returns.")
            
            # Gecikme etkisi yorumu
            if abs(best_corr) > 0.3:
                direction = "positive" if best_corr > 0 else "inverse"
                patterns['findings'].append(f"News sentiment shows a {direction} correlation with price movements {best_lag} day(s) later.")
            
            # Fark yorumu
            if max_return_diff > 1.0:  # %1'den fazla fark
                patterns['findings'].append(f"The difference in returns between positive and negative news is most pronounced {max_diff_lag} day(s) after publication.")
            
            return patterns
            
        except Exception as e:
            logger.error(f"Haber etkisi örüntüleri analiz edilirken hata: {str(e)}")
            return {}
    
    def create_sentiment_scenarios(self, symbol, forecast_days=30):
        """
        Farklı haber duyarlılığı senaryolarına göre tahminler oluşturur
        """
        try:
            # Önbelleği kontrol et
            cache_key = f"sentiment_scenarios_{symbol}_{forecast_days}"
            cached_scenarios = self.ml_cache.get(cache_key)
            
            if cached_scenarios:
                logger.info(f"Önbellekten {symbol} için duygu senaryoları alınıyor")
                return cached_scenarios
            
            # Tam analiz verilerini al
            data = self.data_processor.get_complete_analysis_data(symbol, days_back=max(60, forecast_days*2))
            
            if not data or 'prophet_data' not in data or data['prophet_data'] is None:
                logger.error(f"{symbol} için Prophet verisi hazırlanamadı")
                return {
                    "error": f"Failed to prepare data for {symbol}",
                    "status": "error"
                }
            
            # Veri seti sentimant içeriyor mu kontrol et
            if 'sentiment' not in data['prophet_data'].columns:
                logger.warning(f"{symbol} için duygu verisi yok")
                return {
                    "error": f"No sentiment data available for {symbol}",
                    "status": "error"
                }
            
            # Haber duyarlılığı içeren zenginleştirilmiş model
            model = NewsEnhancedProphetModel()
            prophet_df = data['prophet_data']
            
            # Mevcut ortalama duyarlılık
            current_sentiment = prophet_df['sentiment'].mean()
            
            # Modeli oluştur ve eğit
            model.build_enhanced_model()
            model.fit(prophet_df)
            
            # Senaryo tahminleri
            scenarios = {
                'very_negative': -0.8,
                'negative': -0.4,
                'neutral': 0.0,
                'positive': 0.4,
                'very_positive': 0.8
            }
            
            scenario_results = {}
            
            for name, sentiment_value in scenarios.items():
                # Sentiment değeri ile tahmin yap
                forecast = model.predict_with_future_sentiment(periods=forecast_days, future_sentiment=sentiment_value)
                
                if forecast is not None:
                    # Son tarih ve değerleri al
                    last_date = forecast['ds'].max()
                    last_forecast = forecast[forecast['ds'] == last_date]['yhat'].values[0]
                    lower_bound = forecast[forecast['ds'] == last_date]['yhat_lower'].values[0]
                    upper_bound = forecast[forecast['ds'] == last_date]['yhat_upper'].values[0]
                    
                    # Günlük tahminleri ekle
                    daily_forecasts = []
                    
                    for i, row in forecast[forecast['ds'] > datetime.now()].iterrows():
                        daily_forecasts.append({
                            'date': row['ds'].strftime('%Y-%m-%d'),
                            'price': float(row['yhat']),
                            'lower_bound': float(row['yhat_lower']),
                            'upper_bound': float(row['yhat_upper'])
                        })
                    
                    # Son gerçek değer
                    last_actual = prophet_df['y'].iloc[-1]
                    
                    # Değişim yüzdesi
                    percent_change = ((last_forecast - last_actual) / last_actual) * 100
                    
                    scenario_results[name] = {
                        'sentiment_value': sentiment_value,
                        'forecasted_price': float(last_forecast),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound),
                        'percent_change': float(percent_change),
                        'daily_forecasts': daily_forecasts
                    }
            
            # Sonuç
            result = {
                'symbol': symbol,
                'current_price': float(prophet_df['y'].iloc[-1]),
                'current_sentiment': float(current_sentiment),
                'forecast_days': forecast_days,
                'scenarios': scenario_results,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            # Önbelleğe al (6 saat süreyle)
            self.ml_cache.set(cache_key, result, 6 * 3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Duygu senaryoları oluşturulurken hata: {str(e)}")
            return {
                "error": f"Failed to create sentiment scenarios for {symbol}: {str(e)}",
                "status": "error"
            }