# backend/apps/news/sentiment/visualizers.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SentimentVisualizer:
    """
    Duygu analizi sonuçlarını görselleştirmek için temel sınıf
    """
    
    def __init__(self, dark_mode=False):
        self.dark_mode = dark_mode
        self._setup_style()
    
    def _setup_style(self):
        """
        Görselleştirme stillerini ayarla
        """
        if self.dark_mode:
            plt.style.use('dark_background')
            self.colors = {
                'positive': '#4CAF50',  # Yeşil
                'negative': '#F44336',  # Kırmızı
                'neutral': '#9E9E9E',   # Gri
                'background': '#121212',
                'text': '#FFFFFF'
            }
        else:
            plt.style.use('seaborn-v0_8-whitegrid')
            self.colors = {
                'positive': '#4CAF50',  # Yeşil
                'negative': '#F44336',  # Kırmızı
                'neutral': '#9E9E9E',   # Gri
                'background': '#FFFFFF',
                'text': '#000000'
            }
    
    def _figure_to_base64(self, fig):
        """
        Matplotlib figürünü base64 kodlu resme dönüştür
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_str
    
    def generate_visualization(self, data):
        """
        Alt sınıflar tarafından uygulanacak görselleştirme metodu
        """
        raise NotImplementedError("Alt sınıflar bu metodu uygulamalıdır")

class SentimentDistributionVisualizer(SentimentVisualizer):
    """
    Duygu durumu dağılımını görselleştiren sınıf
    """
    
    def generate_visualization(self, sentiment_counts):
        """
        Pozitif, negatif ve nötr duygu dağılımını pasta grafiği olarak gösterir
        """
        try:
            # Veriyi hazırla
            labels = ['Positive', 'Negative', 'Neutral']
            sizes = [
                sentiment_counts.get('positive', 0),
                sentiment_counts.get('negative', 0),
                sentiment_counts.get('neutral', 0)
            ]
            
            # Sıfır değerlerinin olduğu kategorileri kaldır
            non_zero_indices = [i for i, size in enumerate(sizes) if size > 0]
            filtered_labels = [labels[i] for i in non_zero_indices]
            filtered_sizes = [sizes[i] for i in non_zero_indices]
            
            if not filtered_sizes:
                return None
            
            # Pasta grafiği oluştur
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = [self.colors['positive'], self.colors['negative'], self.colors['neutral']]
            filtered_colors = [colors[i] for i in non_zero_indices]
            
            wedges, texts, autotexts = ax.pie(
                filtered_sizes, 
                labels=None, 
                autopct='%1.1f%%',
                colors=filtered_colors,
                startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1}
            )
            
            # Metinleri formatla
            for i, autotext in enumerate(autotexts):
                autotext.set_color('white')
                autotext.set_fontsize(11)
            
            # Başlık ve açıklamalar
            ax.set_title('Sentiment Distribution', fontsize=16, pad=20)
            
            # Açıklama ekle
            ax.legend(wedges, filtered_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            return self._figure_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error generating sentiment distribution visualization: {str(e)}")
            return None

class SentimentTimeSeriesVisualizer(SentimentVisualizer):
    """
    Zaman serisi olarak duygu değişimini görselleştiren sınıf
    """
    
    def generate_visualization(self, trends_data):
        """
        Zaman içindeki duygu skorlarını çizgi grafiği olarak gösterir
        """
        try:
            # Veriyi DataFrame'e dönüştür
            df = pd.DataFrame(trends_data)
            
            if df.empty:
                return None
            
            # Tarih sütununu datetime formatına dönüştür
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Görselleştirme
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Renk haritası oluştur
            norm = plt.Normalize(-1, 1)
            cmap = plt.cm.RdYlGn  # Kırmızı-Sarı-Yeşil renk haritası
            
            # Skoru çiz
            scatter = ax.scatter(
                df['date'], 
                df['score'], 
                c=df['score'], 
                cmap=cmap, 
                norm=norm, 
                alpha=0.7, 
                s=80
            )
            
            # Noktaları çizgiyle bağla
            ax.plot(df['date'], df['score'], color='gray', alpha=0.6, linestyle='-', linewidth=1)
            
            # Eksen formatları
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Sentiment Score', fontsize=12)
            ax.set_title('Sentiment Trend Over Time', fontsize=16)
            
            # y ekseni -1 ile 1 arasında sabit
            ax.set_ylim(-1, 1)
            
            # x ekseni belli aralıklarla gösterilsin
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
            
            # Renk çubuğu ekle
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Sentiment Score (Negative to Positive)', fontsize=10)
            
            # Nötr çizgisini ekle
            ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            
            # Açıklama ekle
            ax.text(0.02, 0.95, 'Positive', transform=ax.transAxes, fontsize=11, color=self.colors['positive'])
            ax.text(0.02, 0.05, 'Negative', transform=ax.transAxes, fontsize=11, color=self.colors['negative'])
            
            plt.tight_layout()
            plt.xticks(rotation=45)
            
            return self._figure_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error generating sentiment time series visualization: {str(e)}")
            return None

class StockSentimentCorrelationVisualizer(SentimentVisualizer):
    """
    Hisse senedi fiyatları ile duygu skorları arasındaki korelasyonu görselleştiren sınıf
    """
    
    def generate_visualization(self, sentiment_data, stock_data):
        """
        Hisse senedi fiyatları ile duygu skorları arasındaki korelasyonu gösterir
        """
        try:
            # Veriyi hazırla
            sentiment_df = pd.DataFrame(sentiment_data)
            stock_df = pd.DataFrame(stock_data)
            
            if sentiment_df.empty or stock_df.empty:
                return None
            
            # Tarih sütunlarını datetime formatına dönüştür
            sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
            stock_df['date'] = pd.to_datetime(stock_df['date'])
            
            # İki veri setini tarih üzerinden birleştir
            merged_df = pd.merge(sentiment_df, stock_df, on='date', how='inner')
            
            if merged_df.empty:
                return None
            
            # Görselleştirme
            fig, ax1 = plt.subplots(figsize=(12, 6))
            
            # Hisse fiyatı için
            color = 'tab:blue'
            ax1.set_xlabel('Date', fontsize=12)
            ax1.set_ylabel('Stock Price', color=color, fontsize=12)
            ax1.plot(merged_df['date'], merged_df['close'], color=color, linewidth=2, label='Stock Price')
            ax1.tick_params(axis='y', labelcolor=color)
            
            # Duygu skoru için ikinci y ekseni
            ax2 = ax1.twinx()
            color = 'tab:red'
            ax2.set_ylabel('Sentiment Score', color=color, fontsize=12)
            ax2.plot(merged_df['date'], merged_df['score'], color=color, linewidth=2, linestyle='--', label='Sentiment Score')
            ax2.tick_params(axis='y', labelcolor=color)
            
            # Başlık
            plt.title('Stock Price vs Sentiment Score', fontsize=16)
            
            # Açıklamaları birleştir
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # x ekseni formatı
            ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            return self._figure_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error generating stock sentiment correlation visualization: {str(e)}")
            return None

class WordCloudVisualizer(SentimentVisualizer):
    """
    Haber metinlerindeki yaygın kelimeleri kelime bulutu olarak görselleştiren sınıf
    """
    
    def generate_visualization(self, news_texts, title="Common Words in Financial News"):
        """
        Haber metinlerinden kelime bulutu oluşturur
        """
        try:
            from wordcloud import WordCloud
            from nltk.corpus import stopwords
            import nltk
            
            # NLTK kaynakları indir
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')
            
            # Tüm metinleri birleştir
            text = ' '.join(news_texts)
            
            if not text:
                return None
            
            # Durma kelimelerini ayarla
            stop_words = set(stopwords.words('english'))
            financial_stop_words = {'said', 'also', 'would', 'one', 'may', 'new', 'will', 'says'}
            stop_words.update(financial_stop_words)
            
            # Kelime bulutu oluştur
            wc = WordCloud(
                background_color=self.colors['background'],
                max_words=100,
                stopwords=stop_words,
                width=800, 
                height=400,
                colormap='viridis',
                contour_width=1,
                contour_color='steelblue'
            )
            
            word_cloud = wc.generate(text)
            
            # Görselleştir
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.imshow(word_cloud, interpolation='bilinear')
            ax.set_title(title, fontsize=16, pad=20)
            ax.axis("off")
            
            plt.tight_layout()
            
            return self._figure_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error generating word cloud visualization: {str(e)}")
            return None

class MultipleVisualizationsGenerator:
    """
    Birden fazla görselleştirmeyi üreten ve birleştiren yardımcı sınıf
    """
    
    def __init__(self, dark_mode=False):
        self.dark_mode = dark_mode
        self.visualizers = {
            'distribution': SentimentDistributionVisualizer(dark_mode),
            'time_series': SentimentTimeSeriesVisualizer(dark_mode),
            'correlation': StockSentimentCorrelationVisualizer(dark_mode),
            'word_cloud': WordCloudVisualizer(dark_mode)
        }
    
    def generate_all_visualizations(self, sentiment_data, stock_data=None, news_texts=None):
        """
        Tüm görselleştirmeleri üretir ve döndürür
        """
        results = {}
        
        # Duygu dağılımı
        if 'sentiment_counts' in sentiment_data:
            results['sentiment_distribution'] = self.visualizers['distribution'].generate_visualization(
                sentiment_data['sentiment_counts']
            )
        
        # Zaman serisi
        if 'trends' in sentiment_data:
            results['sentiment_trend'] = self.visualizers['time_series'].generate_visualization(
                sentiment_data['trends']
            )
        
        # Hisse senedi korelasyonu
        if stock_data and 'trends' in sentiment_data:
            results['stock_correlation'] = self.visualizers['correlation'].generate_visualization(
                sentiment_data['trends'], stock_data
            )
        
        # Kelime bulutu
        if news_texts:
            results['word_cloud'] = self.visualizers['word_cloud'].generate_visualization(
                news_texts
            )
        
        return results
