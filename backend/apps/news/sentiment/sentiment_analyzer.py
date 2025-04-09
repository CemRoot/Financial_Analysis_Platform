# backend/apps/news/sentiment/sentiment_analyzer.py

import logging
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as VaderSentimentAnalyzer
from django.conf import settings

# Gerekli NLTK kaynaklarını yükle
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)

class FinancialNewsAnalyzer:
    """
    Finansal haberler için gelişmiş duygu analizi ve içerik işleme
    Bu sınıf, finansal haberlerin olumlu/olumsuz/nötr duygu analizini yapar,
    önem derecelerini belirler ve haber içeriğinden anahtar bilgileri çıkarır.
    """
    
    def __init__(self):
        self.vader = VaderSentimentAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # Finansal terimler sözlüğü
        self.financial_lexicon = {
            'positive': [
                'beat', 'exceeded', 'surge', 'bullish', 'rally', 'growth', 'profit', 'gain', 
                'rise', 'up', 'increase', 'higher', 'positive', 'strong', 'opportunity', 'outperform',
                'upside', 'recovery', 'boom', 'breakthrough', 'upgrade', 'raised', 'record', 'success'
            ],
            'negative': [
                'miss', 'fell', 'bearish', 'decline', 'drop', 'loss', 'down', 'decrease', 'lower',
                'negative', 'weak', 'risk', 'underperform', 'downside', 'recession', 'bust', 'downgrade',
                'lowered', 'disappointing', 'bankruptcy', 'debt', 'litigation', 'investigation', 'recall'
            ],
            'neutral': [
                'unchanged', 'flat', 'steady', 'stable', 'announced', 'reported', 'said', 'expected',
                'estimated', 'projected', 'forecasted', 'plan', 'strategy', 'outlook', 'guidance'
            ]
        }
        
        # Finansal olaylar için anahtar kelimeler
        self.event_keywords = {
            'earnings': ['earnings', 'revenue', 'profit', 'income', 'eps', 'quarter', 'guidance', 'outlook'],
            'merger_acquisition': ['merger', 'acquisition', 'takeover', 'buyout', 'purchase', 'acquire', 'bid', 'deal'],
            'product_launch': ['launch', 'unveil', 'introduce', 'announce', 'release', 'new product', 'innovation'],
            'leadership_change': ['ceo', 'executive', 'appoint', 'resign', 'management', 'director', 'board', 'leadership'],
            'legal_regulatory': ['lawsuit', 'settlement', 'fine', 'penalty', 'regulation', 'compliance', 'investigation'],
            'market_trend': ['market', 'trend', 'sector', 'industry', 'economy', 'interest rate', 'inflation', 'recession']
        }
    
    def preprocess_text(self, text):
        """
        Metin önişleme (HTML kaldırma, özel karakterler, küçük harfe çevirme vb.)
        """
        if not text:
            return ""
            
        # HTML etiketlerini kaldır
        text = re.sub(r'<.*?>', ' ', text)
        
        # URL'leri kaldır
        text = re.sub(r'http\S+', ' ', text)
        
        # Özel karakterleri kaldır ve küçük harfe çevir
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_sentiment_score(self, text, method='combined'):
        """
        Metin için duygu puanı hesaplar (farklı yöntemlerle)
        
        method:
        - 'vader': VADER duygu analizi
        - 'textblob': TextBlob duygu analizi
        - 'lexicon': Finansal terimler sözlüğü tabanlı analiz
        - 'combined': Tüm yöntemlerin ağırlıklı ortalaması (varsayılan)
        
        Dönüş değeri: -1 (çok olumsuz) ile 1 (çok olumlu) arasında bir değer
        """
        if not text:
            return 0
        
        preprocessed_text = self.preprocess_text(text)
        
        if method == 'vader':
            scores = self.vader.polarity_scores(preprocessed_text)
            return scores['compound']
        
        elif method == 'textblob':
            blob = TextBlob(preprocessed_text)
            # TextBlob -1 ile 1 arasında değer döndürür
            return blob.sentiment.polarity
        
        elif method == 'lexicon':
            # Metni kelimelere ayır
            words = word_tokenize(preprocessed_text)
            words = [word for word in words if word not in self.stop_words]
            
            # Pozitif ve negatif kelime sayısını hesapla
            positive_count = sum(1 for word in words if word in self.financial_lexicon['positive'])
            negative_count = sum(1 for word in words if word in self.financial_lexicon['negative'])
            total_count = positive_count + negative_count
            
            # Skor hesapla
            if total_count == 0:
                return 0
            return (positive_count - negative_count) / total_count
        
        elif method == 'combined':
            # Tüm yöntemleri uygula ve ağırlıklı ortalama al
            vader_score = self.get_sentiment_score(text, 'vader')
            textblob_score = self.get_sentiment_score(text, 'textblob')
            lexicon_score = self.get_sentiment_score(text, 'lexicon')
            
            # VADER'a daha fazla ağırlık ver
            return 0.5 * vader_score + 0.3 * textblob_score + 0.2 * lexicon_score
        
        else:
            logger.warning(f"Bilinmeyen duygu analizi yöntemi: {method}")
            return 0
    
    def analyze_news_importance(self, news):
        """
        Haberin önem derecesini belirler
        
        Önem faktörleri:
        - Kaynak güvenilirliği (source_ranking)
        - Haber uzunluğu
        - Başlıkta şirket adı/sembolü geçmesi
        - Belirli anahtar olayların geçmesi (kazanç raporu, birleşme, ürün lansmanı vb.)
        
        Dönüş değeri: 0 (önemsiz) ile 1 (çok önemli) arasında bir değer
        """
        if not news:
            return 0
        
        importance_score = 0.5  # Başlangıç değeri
        
        # Kaynak güvenilirliği
        source_ranking = news.get('source_ranking', 0)
        if isinstance(source_ranking, (int, float)):
            # Kaynak puanını 0-1 aralığına normalleştir (10 ise çok güvenilir, 1 ise az güvenilir)
            source_importance = min(10, max(1, source_ranking)) / 10
            importance_score += 0.3 * source_importance
        
        # Haber metni
        title = news.get('title', '')
        content = news.get('content', '')
        full_text = f"{title} {content}"
        
        # Metin uzunluğu (100 kelime ve üzeri ise tam puan)
        text_length = len(word_tokenize(self.preprocess_text(full_text)))
        length_score = min(1.0, text_length / 100)
        importance_score += 0.1 * length_score
        
        # Başlıkta şirket sembolü/adı geçmesi
        symbol = news.get('symbol', '')
        company = news.get('company', '')
        
        if symbol and symbol.upper() in title.upper():
            importance_score += 0.2
        elif company and company.upper() in title.upper():
            importance_score += 0.15
        
        # Önemli finansal olaylar
        event_score = 0
        for event_type, keywords in self.event_keywords.items():
            for keyword in keywords:
                if keyword in full_text.lower():
                    # Kazanç raporları ve birleşmeler daha önemli
                    if event_type in ['earnings', 'merger_acquisition']:
                        event_score += 0.1
                    else:
                        event_score += 0.05
                    break  # Her olay kategorisinden en fazla bir kez puan al
        
        # Maksimum 0.3 puan ekle
        importance_score += min(0.3, event_score)
        
        # 0-1 aralığına normalleştir
        return min(1.0, max(0.0, importance_score))
    
    def detect_event_type(self, text):
        """
        Haber metninden olay türünü belirler
        """
        if not text:
            return None
            
        preprocessed_text = self.preprocess_text(text)
        event_counts = {}
        
        for event_type, keywords in self.event_keywords.items():
            event_counts[event_type] = 0
            for keyword in keywords:
                if keyword in preprocessed_text:
                    event_counts[event_type] += 1
        
        # En çok anahtar kelime içeren olay türünü bul
        max_count = max(event_counts.values())
        if max_count == 0:
            return None
            
        # Eğer birden fazla aynı sayıda anahtar kelime içeren olay varsa, öncelik sırasına göre seç
        priority_order = ['earnings', 'merger_acquisition', 'product_launch', 'leadership_change', 'legal_regulatory', 'market_trend']
        for event in priority_order:
            if event_counts[event] == max_count:
                return event
        
        return None
    
    def extract_key_metrics(self, text):
        """
        Haber metninden önemli finansal metrikleri çıkarır (ör. EPS, gelir, büyüme oranı)
        """
        if not text:
            return {}
            
        metrics = {}
        
        # Para değerleri ($X.XX milyon/milyar)
        money_pattern = r'\$(\d+(?:\.\d+)?)\s*(million|billion|m|b|M|B)?'
        money_matches = re.findall(money_pattern, text)
        
        if money_matches:
            metrics['monetary_values'] = []
            for amount, unit in money_matches:
                try:
                    value = float(amount)
                    if unit.lower() in ['million', 'm']:
                        value *= 1000000
                    elif unit.lower() in ['billion', 'b']:
                        value *= 1000000000
                    metrics['monetary_values'].append(value)
                except ValueError:
                    continue
        
        # Yüzde değerleri
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*(%|percent)'
        percentage_matches = re.findall(percentage_pattern, text)
        
        if percentage_matches:
            metrics['percentages'] = []
            for amount, _ in percentage_matches:
                try:
                    value = float(amount)
                    metrics['percentages'].append(value)
                except ValueError:
                    continue
        
        # EPS değerleri
        eps_pattern = r'EPS\s+(?:of)?\s+\$?(\d+(?:\.\d+)?)'
        eps_matches = re.findall(eps_pattern, text, re.IGNORECASE)
        
        if eps_matches:
            try:
                metrics['eps'] = float(eps_matches[0])
            except ValueError:
                pass
        
        # Gelir/satış değerleri
        revenue_pattern = r'revenue\s+(?:of)?\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|m|b|M|B)?'
        revenue_matches = re.findall(revenue_pattern, text, re.IGNORECASE)
        
        if revenue_matches:
            try:
                amount, unit = revenue_matches[0]
                value = float(amount)
                if unit.lower() in ['million', 'm']:
                    value *= 1000000
                elif unit.lower() in ['billion', 'b']:
                    value *= 1000000000
                metrics['revenue'] = value
            except (ValueError, IndexError):
                pass
        
        return metrics
    
    def analyze_news_batch(self, news_list):
        """
        Bir dizi haberi analiz eder ve zenginleştirilmiş sonuçlar döndürür
        """
        if not news_list:
            return []
            
        analyzed_news = []
        
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            description = news.get('description', '')
            
            # İçerik yoksa açıklamayı kullan
            if not content and description:
                content = description
                
            full_text = f"{title} {content}"
            
            # Temel analiz
            sentiment_score = self.get_sentiment_score(full_text)
            importance_score = self.analyze_news_importance(news)
            event_type = self.detect_event_type(full_text)
            key_metrics = self.extract_key_metrics(full_text)
            
            # Zenginleştirilmiş haberi oluştur
            enriched_news = news.copy()
            
            enriched_news.update({
                'sentiment_score': sentiment_score,
                'importance_score': importance_score,
                'weighted_sentiment': sentiment_score * importance_score,
                'event_type': event_type,
                'key_metrics': key_metrics,
                'sentiment_category': 'positive' if sentiment_score > 0.2 else 'negative' if sentiment_score < -0.2 else 'neutral'
            })
            
            analyzed_news.append(enriched_news)
        
        return analyzed_news
    
    def generate_daily_sentiment_data(self, news_list):
        """
        Haber listesinden günlük duygu skorları oluşturur
        """
        if not news_list:
            return pd.DataFrame()
            
        # Haberleri Pandas DataFrame'e dönüştür
        df = pd.DataFrame(news_list)
        
        # Tarih sütunu yoksa published_at/datetime/date sütunlarına bak
        date_column = None
        for column in ['date', 'published_at', 'dateTime', 'datetime']:
            if column in df.columns:
                date_column = column
                break
                
        if not date_column:
            logger.error("Haber listesinde tarih sütunu bulunamadı")
            return pd.DataFrame()
            
        # Tarihi datetime'a dönüştür
        df['date'] = pd.to_datetime(df[date_column])
        
        # Günlük ortalama değerleri hesapla
        daily_data = df.groupby(df['date'].dt.date).agg({
            'sentiment_score': 'mean',
            'importance_score': 'mean',
            'weighted_sentiment': 'mean',
            'title': 'count'  # Haber sayısı
        }).reset_index()
        
        # Sütun isimlerini yeniden adlandır
        daily_data.rename(columns={'title': 'news_count'}, inplace=True)
        
        return daily_data
    
    def compute_sentiment_trends(self, daily_data, window=7):
        """
        Günlük duygu verilerinden trend analizleri yapar
        """
        if daily_data.empty:
            return pd.DataFrame()
            
        # Hareketli ortalama ve değişim hesapla
        df = daily_data.copy()
        df['sentiment_ma'] = df['sentiment_score'].rolling(window=window).mean()
        df['weighted_sentiment_ma'] = df['weighted_sentiment'].rolling(window=window).mean()
        
        # Değişim (eğim) hesapla
        df['sentiment_change'] = df['sentiment_score'].diff()
        df['weighted_sentiment_change'] = df['weighted_sentiment'].diff()
        
        # 7 günlük değişim yüzdesi
        df['sentiment_pct_change_7d'] = df['sentiment_score'].pct_change(periods=min(7, len(df)-1))
        
        # Haber sıklığındaki değişim
        df['news_count_ma'] = df['news_count'].rolling(window=window).mean()
        df['news_count_change'] = df['news_count'].diff()
        
        return df


# Global bir örnek oluştur, bu şekilde uygulama genelinde kullanılabilir
sentiment_analyzer = FinancialNewsAnalyzer()
