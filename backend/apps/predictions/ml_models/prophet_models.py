# backend/apps/predictions/ml_models/prophet_models.py

import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from prophet.plot import plot_plotly, plot_components_plotly
import logging
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from django.conf import settings

logger = logging.getLogger(__name__)

class StockProphetModel:
    """
    Facebook Prophet kütüphanesini kullanarak hisse senedi fiyat tahminleri yapar.
    Bu model mevsimsellik, tatiller ve dış değişkenleri (regressor) kullanabilir.
    """
    
    def __init__(self):
        self.model = None
        self.forecast = None
        self.historical_data = None
        self.model_params = {
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0,
            'seasonality_mode': 'multiplicative',
            'daily_seasonality': False,
            'weekly_seasonality': True,
            'yearly_seasonality': True
        }
    
    def prepare_data(self, stock_data, target_column='close', date_column='date'):
        """
        Prophet için veri hazırlar. 
        Prophet veri sütunları ds (tarih) ve y (hedef değişken) olmalıdır.
        """
        try:
            # Gelen veri bir DataFrame ise doğrudan kullan, liste ise dönüştür
            if isinstance(stock_data, list):
                df = pd.DataFrame(stock_data)
            else:
                df = stock_data.copy()
            
            # Tarihleri datetime türüne çevir
            if isinstance(df[date_column].iloc[0], str):
                df[date_column] = pd.to_datetime(df[date_column])
            
            # Prophet için gereken format
            prophet_df = pd.DataFrame({
                'ds': df[date_column],
                'y': df[target_column]
            })
            
            # Veriyi sakla
            self.historical_data = prophet_df
            
            return prophet_df
        
        except Exception as e:
            logger.error(f"Prophet için veri hazırlanırken hata: {str(e)}")
            return None
    
    def add_regressor_data(self, prophet_df, regressors):
        """
        Prophet modeline dış değişkenler ekler.
        
        regressors: {
            'column_name': {
                'data': Series veya liste,
                'mode': 'additive' veya 'multiplicative',
                'standardize': True veya False
            }
        }
        """
        try:
            # Her bir dış değişkeni ekle
            for column, params in regressors.items():
                data = params.get('data')
                if data is not None:
                    prophet_df[column] = data
            
            return prophet_df
        
        except Exception as e:
            logger.error(f"Regressor eklenirken hata: {str(e)}")
            return prophet_df
    
    def add_sentiment_data(self, prophet_df, sentiment_data):
        """
        Haber duygu analizinden elde edilen verileri regressor olarak ekler
        """
        try:
            # Sentiment verisi tarih ve duygu skoru içermeli
            if isinstance(sentiment_data, pd.DataFrame):
                # Tarih sütunu varsa birleştir
                if 'date' in sentiment_data.columns:
                    sentiment_df = sentiment_data.rename(columns={'date': 'ds'})
                    if isinstance(sentiment_df['ds'].iloc[0], str):
                        sentiment_df['ds'] = pd.to_datetime(sentiment_df['ds'])
                    
                    # Birleştir
                    prophet_df = pd.merge(prophet_df, 
                                          sentiment_df[['ds', 'sentiment']], 
                                          on='ds', 
                                          how='left')
                    
                    # Eksik değerleri doldur
                    prophet_df['sentiment'].fillna(0, inplace=True)
            
            # Liste ise dönüştür
            elif isinstance(sentiment_data, list) and len(sentiment_data) > 0:
                sentiment_df = pd.DataFrame(sentiment_data)
                if 'date' in sentiment_df.columns and 'sentiment' in sentiment_df.columns:
                    sentiment_df['ds'] = pd.to_datetime(sentiment_df['date'])
                    
                    # Birleştir
                    prophet_df = pd.merge(prophet_df, 
                                          sentiment_df[['ds', 'sentiment']], 
                                          on='ds', 
                                          how='left')
                    
                    # Eksik değerleri doldur
                    prophet_df['sentiment'].fillna(0, inplace=True)
            
            return prophet_df
        
        except Exception as e:
            logger.error(f"Sentiment verileri eklenirken hata: {str(e)}")
            return prophet_df
    
    def build_model(self, **kwargs):
        """
        Prophet modelini oluşturur ve özelleştirir
        """
        try:
            # Varsayılan parametreleri güncelle
            for key, value in kwargs.items():
                if key in self.model_params:
                    self.model_params[key] = value
            
            # Modeli oluştur
            self.model = Prophet(
                changepoint_prior_scale=self.model_params['changepoint_prior_scale'],
                seasonality_prior_scale=self.model_params['seasonality_prior_scale'],
                seasonality_mode=self.model_params['seasonality_mode'],
                daily_seasonality=self.model_params['daily_seasonality'],
                weekly_seasonality=self.model_params['weekly_seasonality'],
                yearly_seasonality=self.model_params['yearly_seasonality']
            )
            
            # ABD tatillerini ekle
            self.model.add_country_holidays(country_name='US')
            
            return self.model
        
        except Exception as e:
            logger.error(f"Prophet modeli oluşturulurken hata: {str(e)}")
            return None
    
    def add_regressors(self, regressors):
        """
        Modele dış değişkenler ekler
        
        regressors: {
            'column_name': {
                'mode': 'additive' veya 'multiplicative',
                'standardize': True veya False
            }
        }
        """
        try:
            if self.model is None:
                self.build_model()
            
            # Her bir dış değişkeni modele ekle
            for column, params in regressors.items():
                mode = params.get('mode', 'additive')
                standardize = params.get('standardize', True)
                
                self.model.add_regressor(
                    name=column,
                    mode=mode,
                    standardize=standardize
                )
            
            return self.model
        
        except Exception as e:
            logger.error(f"Regressor eklenirken hata: {str(e)}")
            return self.model
    
    def fit(self, prophet_df):
        """
        Modeli eğitir
        """
        try:
            if self.model is None:
                self.build_model()
            
            # Modeli eğit
            self.model.fit(prophet_df)
            
            return self.model
        
        except Exception as e:
            logger.error(f"Prophet modeli eğitilirken hata: {str(e)}")
            return None
    
    def make_future_dataframe(self, periods, freq='D', include_history=True):
        """
        Tahmin için gelecek tarihler dataframe'i oluşturur
        """
        try:
            if self.model is None:
                logger.error("Model henüz eğitilmemiş")
                return None
            
            future = self.model.make_future_dataframe(
                periods=periods,
                freq=freq,
                include_history=include_history
            )
            
            return future
        
        except Exception as e:
            logger.error(f"Future dataframe oluşturulurken hata: {str(e)}")
            return None
    
    def predict(self, future=None, periods=30):
        """
        Gelecek fiyatları tahmin eder
        """
        try:
            if self.model is None:
                logger.error("Model henüz eğitilmemiş")
                return None
            
            # Future dataframe yoksa oluştur
            if future is None:
                future = self.make_future_dataframe(periods=periods)
            
            # Tahmin yap
            self.forecast = self.model.predict(future)
            
            return self.forecast
        
        except Exception as e:
            logger.error(f"Tahmin yapılırken hata: {str(e)}")
            return None
    
    def forecast_with_regressors(self, future, regressors):
        """
        Dış değişkenlerle gelecek tahminleri yapar
        
        regressors: {
            'column_name': future_values (list or series)
        }
        """
        try:
            if self.model is None:
                logger.error("Model henüz eğitilmemiş")
                return None
            
            # Her bir dış değişkeni future dataframe'e ekle
            for column, values in regressors.items():
                if len(values) != len(future):
                    logger.warning(f"{column} değişkeni için verilen değer sayısı ({len(values)}) ile future frame uzunluğu ({len(future)}) eşleşmiyor.")
                    # Son değeri çoğaltarak eşitle
                    if len(values) > 0:
                        last_value = values[-1]
                        values = list(values) + [last_value] * (len(future) - len(values))
                        future[column] = values[:len(future)]
                else:
                    future[column] = values
            
            # Tahmin yap
            self.forecast = self.model.predict(future)
            
            return self.forecast
        
        except Exception as e:
            logger.error(f"Regressor ile tahmin yapılırken hata: {str(e)}")
            return None
    
    def evaluate_model(self, initial='730 days', period='180 days', horizon='365 days'):
        """
        Modeli çapraz doğrulama ile değerlendirir
        """
        try:
            if self.model is None:
                logger.error("Model henüz eğitilmemiş")
                return None
            
            # Çapraz doğrulama yap
            cv_results = cross_validation(
                model=self.model,
                initial=initial,
                period=period,
                horizon=horizon
            )
            
            # Performans metriklerini hesapla
            metrics = performance_metrics(cv_results)
            
            return {
                'cv_results': cv_results,
                'metrics': metrics
            }
        
        except Exception as e:
            logger.error(f"Model değerlendirilirken hata: {str(e)}")
            return None
    
    def save_model(self, path=None, model_name='prophet_stock_model'):
        """
        Modeli kaydeder
        """
        try:
            if self.model is None:
                logger.error("Kaydedilecek model yok")
                return False
            
            # Varsayılan kayıt yolu
            if path is None:
                path = os.path.join(settings.ML_MODELS_DIR, f'{model_name}.json')
            
            # Modeli JSON formatında kaydet
            with open(path, 'w') as f:
                json.dump(model_to_json(self.model), f)
            
            logger.info(f"Model başarıyla kaydedildi: {path}")
            return True
        
        except Exception as e:
            logger.error(f"Model kaydedilirken hata: {str(e)}")
            return False
    
    def load_model(self, path=None, model_name='prophet_stock_model'):
        """
        Kaydedilmiş modeli yükler
        """
        try:
            # Varsayılan yükleme yolu
            if path is None:
                path = os.path.join(settings.ML_MODELS_DIR, f'{model_name}.json')
            
            # JSON'dan modeli yükle
            with open(path, 'r') as f:
                model_json = json.load(f)
            
            self.model = model_from_json(model_json)
            
            logger.info(f"Model başarıyla yüklendi: {path}")
            return self.model
        
        except Exception as e:
            logger.error(f"Model yüklenirken hata: {str(e)}")
            return None
    
    def plot_forecast(self, plot_components=False, uncertainty=True):
        """
        Tahmin grafiklerini oluşturur
        """
        try:
            if self.forecast is None:
                logger.error("Henüz tahmin yapılmamış")
                return None
            
            # Temel tahmin grafiği
            fig1 = self.model.plot(self.forecast)
            
            # Bileşen grafiği isteniyorsa oluştur
            fig2 = None
            if plot_components:
                fig2 = self.model.plot_components(self.forecast)
            
            return {
                'forecast_plot': fig1,
                'components_plot': fig2
            }
        
        except Exception as e:
            logger.error(f"Tahmin grafiği oluşturulurken hata: {str(e)}")
            return None
    
    def create_interactive_plot(self, symbol=None, include_sentiment=False):
        """
        Plotly ile interaktif tahmin grafiği oluşturur
        """
        try:
            if self.forecast is None or self.historical_data is None:
                logger.error("Tahmin veya geçmiş veri yok")
                return None
            
            # Gerçek ve tahmin verilerini birleştir
            forecast_subset = self.forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            merged = pd.merge(forecast_subset, self.historical_data, on='ds', how='left')
            
            # Plotly ile interaktif grafik
            fig = make_subplots(specs=[[{"secondary_y": include_sentiment}]])
            
            # Gerçek değerler
            fig.add_trace(
                go.Scatter(
                    x=merged['ds'],
                    y=merged['y'],
                    name="Gerçek Fiyat",
                    line=dict(color='royalblue'),
                    hovertemplate='%{x}<br>Fiyat: %{y:.2f}<extra></extra>'
                ),
                secondary_y=False
            )
            
            # Tahmin değerleri
            fig.add_trace(
                go.Scatter(
                    x=merged['ds'],
                    y=merged['yhat'],
                    name="Tahmin",
                    line=dict(color='firebrick'),
                    hovertemplate='%{x}<br>Tahmin: %{y:.2f}<extra></extra>'
                ),
                secondary_y=False
            )
            
            # Tahmin aralığı
            fig.add_trace(
                go.Scatter(
                    x=merged['ds'],
                    y=merged['yhat_upper'],
                    name="Üst Sınır",
                    line=dict(width=0),
                    showlegend=False,
                    hovertemplate='%{x}<br>Üst: %{y:.2f}<extra></extra>'
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=merged['ds'],
                    y=merged['yhat_lower'],
                    name="Alt Sınır",
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(255, 0, 0, 0.1)',
                    showlegend=False,
                    hovertemplate='%{x}<br>Alt: %{y:.2f}<extra></extra>'
                ),
                secondary_y=False
            )
            
            # Duygu skoru varsa ekle
            if include_sentiment and 'sentiment' in merged.columns:
                fig.add_trace(
                    go.Scatter(
                        x=merged['ds'],
                        y=merged['sentiment'],
                        name="Duygu Skoru",
                        line=dict(color='green', dash='dash'),
                        hovertemplate='%{x}<br>Duygu: %{y:.2f}<extra></extra>'
                    ),
                    secondary_y=True
                )
            
            # Grafik başlık ve etiketleri
            title = f"{symbol} Hisse Senedi Fiyat Tahmini" if symbol else "Hisse Senedi Fiyat Tahmini"
            fig.update_layout(
                title=title,
                xaxis_title="Tarih",
                yaxis_title="Fiyat",
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            if include_sentiment:
                fig.update_yaxes(title_text="Duygu Skoru", secondary_y=True)
            
            return fig
        
        except Exception as e:
            logger.error(f"İnteraktif grafik oluşturulurken hata: {str(e)}")
            return None
    
    def format_results(self, symbol, forecast_days=30):
        """
        Tahmin sonuçlarını API'den dönecek formatta hazırlar
        """
        try:
            if self.forecast is None:
                logger.error("Henüz tahmin yapılmamış")
                return None
            
            # Geçmiş verilerdeki son gerçek değer
            if self.historical_data is not None and not self.historical_data.empty:
                last_real_date = self.historical_data['ds'].max()
                last_real_value = self.historical_data[self.historical_data['ds'] == last_real_date]['y'].values[0]
            else:
                # Geçmiş veri yoksa forecast'taki ilk değeri kullan
                last_real_date = self.forecast['ds'].min()
                last_real_value = self.forecast[self.forecast['ds'] == last_real_date]['yhat'].values[0]
            
            # Gelecek tahminleri
            future_forecast = self.forecast[self.forecast['ds'] > last_real_date].copy()
            
            if future_forecast.empty:
                logger.warning("Gelecek tahminleri bulunamadı")
                return None
            
            # Son tahmin değeri
            end_date = future_forecast['ds'].max()
            end_forecast = future_forecast[future_forecast['ds'] == end_date]
            last_forecast = end_forecast['yhat'].values[0]
            lower_bound = end_forecast['yhat_lower'].values[0]
            upper_bound = end_forecast['yhat_upper'].values[0]
            
            # Değişim yüzdesi
            percent_change = ((last_forecast - last_real_value) / last_real_value) * 100
            
            # Tüm tahmin periyodunu içeren sözlük listesi
            daily_forecasts = []
            
            for _, row in future_forecast.iterrows():
                daily_forecasts.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'price': float(row['yhat']),
                    'lower_bound': float(row['yhat_lower']),
                    'upper_bound': float(row['yhat_upper'])
                })
            
            # Özet sonuçları içeren sözlük
            result = {
                'symbol': symbol,
                'current_price': float(last_real_value),
                'forecast_end_date': end_date.strftime('%Y-%m-%d'),
                'forecasted_price': float(last_forecast),
                'price_change': float(last_forecast - last_real_value),
                'percent_change': float(percent_change),
                'confidence_interval': {
                    'lower': float(lower_bound),
                    'upper': float(upper_bound)
                },
                'uncertainty_range': float(upper_bound - lower_bound),
                'forecast_days': forecast_days,
                'daily_forecasts': daily_forecasts,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Sonuçlar formatlanırken hata: {str(e)}")
            return None


class NewsEnhancedProphetModel(StockProphetModel):
    """
    Haber duyarlılık analizi ile zenginleştirilmiş Prophet modeli.
    Bu model, standart Prophet modelini haber duygu analizi sonuçlarıyla genişletir.
    """
    
    def __init__(self):
        super().__init__()
        self.news_data = None
        self.sentiment_scores = None
    
    def add_news_data(self, news_data):
        """
        Haber verilerini modele ekler ve duygu skorlarını hesaplar
        """
        try:
            self.news_data = news_data
            
            # Haberleri tarihlerine göre grupla ve duygu skorlarını hesapla
            if isinstance(news_data, list) and len(news_data) > 0:
                # Liste verisini DataFrame'e dönüştür
                news_df = pd.DataFrame(news_data)
                
                # 'date' ve 'sentiment' sütunları varsa doğrudan kullan
                if 'date' in news_df.columns and 'sentiment' in news_df.columns:
                    # Tarihi datetime türüne çevir
                    if isinstance(news_df['date'].iloc[0], str):
                        news_df['date'] = pd.to_datetime(news_df['date'])
                    
                    # Günlük ortalama duygu skorlarını hesapla
                    self.sentiment_scores = news_df.groupby(pd.Grouper(key='date', freq='D'))['sentiment'].mean().reset_index()
                
                # Haberleri daha karmaşık bir şekilde işle
                elif 'title' in news_df.columns and 'published_at' in news_df.columns:
                    # Haberleri tarihe göre grupla ve duygu skorlarını kullan veya hesapla
                    news_df['date'] = pd.to_datetime(news_df['published_at']).dt.date
                    
                    # Haber başlık veya içeriğinden duygu analizi eksikse
                    if 'sentiment' not in news_df.columns:
                        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                        analyzer = SentimentIntensityAnalyzer()
                        
                        # Başlık ve içerikten duygu skoru hesapla
                        def get_sentiment(row):
                            text = row.get('title', '') + ' ' + row.get('content', '')
                            sentiment = analyzer.polarity_scores(text)
                            return sentiment['compound']  # -1 ile 1 arası skor
                        
                        news_df['sentiment'] = news_df.apply(get_sentiment, axis=1)
                    
                    # Günlük ortalama duygu skorlarını hesapla
                    self.sentiment_scores = news_df.groupby('date')['sentiment'].mean().reset_index()
                    self.sentiment_scores['date'] = pd.to_datetime(self.sentiment_scores['date'])
            
            elif isinstance(news_data, pd.DataFrame):
                self.sentiment_scores = news_data
            
            return self.sentiment_scores
        
        except Exception as e:
            logger.error(f"Haber verileri eklenirken hata: {str(e)}")
            return None
    
    def prepare_enhanced_data(self, stock_data, sentiment_data=None):
        """
        Hisse senedi verilerini ve haber duygu skorlarını birleştirerek Prophet için veri hazırlar
        """
        try:
            # Önce temel veriyi hazırla
            prophet_df = self.prepare_data(stock_data)
            
            if prophet_df is None:
                return None
            
            # Duygu skorlarını ekle
            if sentiment_data is not None:
                self.add_news_data(sentiment_data)
            
            if self.sentiment_scores is not None:
                prophet_df = self.add_sentiment_data(prophet_df, self.sentiment_scores)
            
            return prophet_df
        
        except Exception as e:
            logger.error(f"Zenginleştirilmiş veri hazırlanırken hata: {str(e)}")
            return None
    
    def build_enhanced_model(self, **kwargs):
        """
        Duygu skoru regressor'ı ile geliştirilmiş bir Prophet modeli oluşturur
        """
        try:
            # Önce temel modeli oluştur
            model = self.build_model(**kwargs)
            
            # Duygu skorunu regressor olarak ekle
            if model is not None:
                self.model.add_regressor('sentiment', standardize=True)
            
            return self.model
        
        except Exception as e:
            logger.error(f"Geliştirilmiş model oluşturulurken hata: {str(e)}")
            return None
    
    def predict_with_future_sentiment(self, periods=30, future_sentiment=None):
        """
        Gelecekteki duygu skorları da dahil edilerek tahmin yapar
        """
        try:
            if self.model is None:
                logger.error("Model henüz eğitilmemiş")
                return None
            
            # Gelecek dataframe'i oluştur
            future = self.make_future_dataframe(periods=periods)
            
            if future is None:
                return None
            
            # Gelecek duygu skorlarını belirle
            if future_sentiment is None and self.sentiment_scores is not None:
                # Son 7 günün ortalamasını gelecek duygu skoru olarak kullan
                recent_sentiment = self.sentiment_scores.tail(7)['sentiment'].mean()
                future['sentiment'] = recent_sentiment
            elif future_sentiment is not None:
                # Direkt olarak verilen değerleri kullan
                if isinstance(future_sentiment, (int, float)):
                    future['sentiment'] = future_sentiment
                elif isinstance(future_sentiment, (list, np.ndarray, pd.Series)):
                    # Liste ise ve uzunluk uygunsa direkt ekle
                    if len(future_sentiment) == len(future):
                        future['sentiment'] = future_sentiment
                    else:
                        # Uzunluk uygun değilse mevcut değerleri doldur ve kalanları son değerle tamamla
                        if len(future_sentiment) > 0:
                            future['sentiment'] = [future_sentiment[min(i, len(future_sentiment)-1)] 
                                                for i in range(len(future))]
                
            # Tahmin yap
            self.forecast = self.model.predict(future)
            
            return self.forecast
        
        except Exception as e:
            logger.error(f"Duygu skorları ile tahmin yapılırken hata: {str(e)}")
            return None
    
    def create_sentiment_impact_analysis(self, symbol, base_sentiment=0):
        """
        Farklı duygu skorlarının fiyat üzerindeki etkisini analiz eder
        """
        try:
            if self.model is None:
                logger.error("Model henüz eğitilmemiş")
                return None
            
            # Farklı duygu skorları için senaryolar oluştur
            sentiment_scenarios = {
                'negative': -0.5,
                'neutral': 0,
                'positive': 0.5,
                'very_positive': 0.8
            }
            
            # Her senaryo için tahminler
            scenario_forecasts = {}
            
            for name, sentiment_value in sentiment_scenarios.items():
                # Gelecek dataframe'i oluştur
                future = self.make_future_dataframe(periods=30)
                
                # Duygu skorunu ekle
                future['sentiment'] = sentiment_value
                
                # Tahmin yap
                forecast = self.model.predict(future)
                
                # Son tarihi al
                last_date = forecast['ds'].max()
                
                # Son değeri depola
                scenario_forecasts[name] = {
                    'sentiment_value': sentiment_value,
                    'forecast': forecast[forecast['ds'] > pd.Timestamp.now()].to_dict('records'),
                    'final_price': float(forecast[forecast['ds'] == last_date]['yhat'].values[0]),
                    'lower_bound': float(forecast[forecast['ds'] == last_date]['yhat_lower'].values[0]),
                    'upper_bound': float(forecast[forecast['ds'] == last_date]['yhat_upper'].values[0])
                }
            
            # Son gerçek değer
            last_real_value = self.historical_data['y'].iloc[-1]
            
            # Senaryo sonuçlarını hazırla
            result = {
                'symbol': symbol,
                'current_price': float(last_real_value),
                'forecast_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'scenarios': scenario_forecasts,
                'baseline_sentiment': base_sentiment,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Duygu etkisi analizi yapılırken hata: {str(e)}")
            return None


# Yardımcı fonksiyonlar (Prophet modelini JSON'a dönüştürmek ve JSON'dan yüklemek için)
def model_to_json(model):
    """Prophet modelini JSON'a dönüştürür"""
    return {
        'growth': model.growth,
        'changepoints': model.changepoints.tolist() if model.changepoints is not None else None,
        'n_changepoints': model.n_changepoints,
        'changepoint_prior_scale': model.changepoint_prior_scale,
        'changepoint_range': model.changepoint_range,
        'yearly_seasonality': model.yearly_seasonality,
        'weekly_seasonality': model.weekly_seasonality,
        'daily_seasonality': model.daily_seasonality,
        'seasonality_mode': model.seasonality_mode,
        'seasonality_prior_scale': model.seasonality_prior_scale,
        'params': model.params.to_dict('records') if hasattr(model, 'params') else None,
        # Diğer parametreler eklenebilir
    }

def model_from_json(model_json):
    """JSON'dan Prophet modeli oluşturur"""
    model = Prophet(
        growth=model_json.get('growth', 'linear'),
        n_changepoints=model_json.get('n_changepoints', 25),
        changepoint_prior_scale=model_json.get('changepoint_prior_scale', 0.05),
        changepoint_range=model_json.get('changepoint_range', 0.8),
        yearly_seasonality=model_json.get('yearly_seasonality', 'auto'),
        weekly_seasonality=model_json.get('weekly_seasonality', 'auto'),
        daily_seasonality=model_json.get('daily_seasonality', 'auto'),
        seasonality_mode=model_json.get('seasonality_mode', 'additive'),
        seasonality_prior_scale=model_json.get('seasonality_prior_scale', 10.0)
    )
    return model