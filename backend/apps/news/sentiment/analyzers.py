# backend/apps/news/sentiment/analyzers.py

import logging
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

# NLTK için gerekli veri setlerini indir
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Haber metinlerinde duygu analizi yapmak için temel sınıf
    """
    
    def __init__(self):
        pass
    
    def analyze(self, text):
        """
        Alt sınıflar tarafından uygulanacak analiz metodu
        """
        raise NotImplementedError("Alt sınıflar bu metodu uygulamalıdır")

class VaderSentimentAnalyzer(SentimentAnalyzer):
    """
    NLTK'nın VADER (Valence Aware Dictionary and sEntiment Reasoner) 
    modelini kullanarak duygu analizi yapan sınıf
    """
    
    def __init__(self):
        super().__init__()
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text):
        """
        VADER ile duygu analizi yaparak polarite skorlarını döndürür
        """
        if not text:
            return {
                'compound': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'sentiment': 'neutral'
            }
            
        try:
            scores = self.analyzer.polarity_scores(text)
            
            # Duygu durumunu belirle
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'compound': compound,
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'sentiment': sentiment
            }
        except Exception as e:
            logger.error(f"VADER sentiment analysis error: {str(e)}")
            return {
                'compound': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'sentiment': 'neutral',
                'error': str(e)
            }

class TextBlobSentimentAnalyzer(SentimentAnalyzer):
    """
    TextBlob kütüphanesini kullanarak duygu analizi yapan sınıf
    """
    
    def __init__(self):
        super().__init__()
    
    def analyze(self, text):
        """
        TextBlob ile duygu analizi yaparak polarite ve öznellik skorlarını döndürür
        """
        if not text:
            return {
                'polarity': 0,
                'subjectivity': 0,
                'sentiment': 'neutral'
            }
            
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Duygu durumunu belirle
            if polarity >= 0.05:
                sentiment = 'positive'
            elif polarity <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment': sentiment
            }
        except Exception as e:
            logger.error(f"TextBlob sentiment analysis error: {str(e)}")
            return {
                'polarity': 0,
                'subjectivity': 0,
                'sentiment': 'neutral',
                'error': str(e)
            }

class CombinedSentimentAnalyzer:
    """
    Birden fazla duygu analizi modelini birleştirerek kullanan sınıf
    """
    
    def __init__(self):
        self.vader_analyzer = VaderSentimentAnalyzer()
        self.textblob_analyzer = TextBlobSentimentAnalyzer()
    
    def analyze(self, text):
        """
        Hem VADER hem de TextBlob'u kullanarak birleştirilmiş duygu analizi yapar
        """
        if not text:
            return {
                'compound': 0,
                'polarity': 0,
                'subjectivity': 0,
                'sentiment': 'neutral'
            }
            
        try:
            vader_results = self.vader_analyzer.analyze(text)
            textblob_results = self.textblob_analyzer.analyze(text)
            
            # Skorların ortalamasını al
            compound = vader_results['compound']
            polarity = textblob_results['polarity']
            avg_score = (compound + polarity) / 2
            
            # Duygu durumunu belirle
            if avg_score >= 0.05:
                sentiment = 'positive'
            elif avg_score <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'compound': compound,
                'polarity': polarity,
                'subjectivity': textblob_results['subjectivity'],
                'vader_sentiment': vader_results['sentiment'],
                'textblob_sentiment': textblob_results['sentiment'],
                'combined_sentiment': sentiment,
                'avg_score': avg_score
            }
        except Exception as e:
            logger.error(f"Combined sentiment analysis error: {str(e)}")
            return {
                'compound': 0,
                'polarity': 0,
                'subjectivity': 0,
                'sentiment': 'neutral',
                'error': str(e)
            }

class NewsSentimentAnalyzer:
    """
    Haber makalelerini analiz eden ve toplu sonuçlar döndüren sınıf
    """
    
    def __init__(self):
        self.analyzer = CombinedSentimentAnalyzer()
    
    def analyze_articles(self, articles):
        """
        Bir dizi haber makalesini analiz eder ve toplu sonuçları döndürür
        """
        if not articles:
            return {
                'sentiment_counts': {'positive': 0, 'negative': 0, 'neutral': 0},
                'average_scores': {'compound': 0, 'polarity': 0, 'subjectivity': 0},
                'articles_analyzed': 0
            }
            
        try:
            results = []
            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                
                # İçerik, açıklama ve başlığı birleştirerek analiz et
                full_text = f"{title} {description} {content}"
                sentiment_result = self.analyzer.analyze(full_text)
                
                # Sonuçları makale bilgileri ile birleştir
                article_result = {
                    'title': title,
                    'url': article.get('url', ''),
                    'published_at': article.get('published_at', ''),
                    'sentiment': sentiment_result
                }
                results.append(article_result)
            
            # Duygu durumu sayımları
            sentiment_counts = Counter([r['sentiment']['combined_sentiment'] for r in results])
            
            # Ortalama skorlar
            compounds = [r['sentiment']['compound'] for r in results]
            polarities = [r['sentiment']['polarity'] for r in results]
            subjectivities = [r['sentiment']['subjectivity'] for r in results]
            
            average_scores = {
                'compound': sum(compounds) / len(compounds) if compounds else 0,
                'polarity': sum(polarities) / len(polarities) if polarities else 0,
                'subjectivity': sum(subjectivities) / len(subjectivities) if subjectivities else 0
            }
            
            return {
                'articles': results,
                'sentiment_counts': dict(sentiment_counts),
                'average_scores': average_scores,
                'articles_analyzed': len(results)
            }
            
        except Exception as e:
            logger.error(f"News sentiment analysis error: {str(e)}")
            return {
                'sentiment_counts': {'positive': 0, 'negative': 0, 'neutral': 0},
                'average_scores': {'compound': 0, 'polarity': 0, 'subjectivity': 0},
                'articles_analyzed': 0,
                'error': str(e)
            }
    
    def analyze_sentiment_trends(self, articles, date_field='published_at'):
        """
        Zaman içindeki duygu trendlerini analiz eder
        """
        if not articles:
            return {'trends': [], 'error': 'No articles to analyze'}
        
        try:
            # Önce tüm makaleleri analiz et
            analyzed_articles = []
            
            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                published_at = article.get(date_field, '')
                
                if not published_at:
                    continue
                
                # ISO formatında tarih dizesini datetime nesnesine dönüştür
                try:
                    if 'T' in published_at:
                        date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    else:
                        date = datetime.strptime(published_at, '%Y-%m-%d')
                except ValueError:
                    continue
                
                # İçerik analizi
                full_text = f"{title} {description} {content}"
                sentiment_result = self.analyzer.analyze(full_text)
                
                analyzed_articles.append({
                    'date': date,
                    'sentiment': sentiment_result['combined_sentiment'],
                    'score': sentiment_result['avg_score']
                })
            
            # Günlük duygu durumlarını topla
            df = pd.DataFrame(analyzed_articles)
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            daily_sentiments = df.groupby('date').agg({
                'score': 'mean',
                'sentiment': lambda x: Counter(x).most_common(1)[0][0]
            }).reset_index()
            
            # Görselleştirme için sonuçları formatlayarak döndür
            trends = daily_sentiments.to_dict('records')
            
            return {
                'trends': trends,
                'total_articles': len(analyzed_articles),
                'period': {
                    'start': min(df['date']).isoformat() if not df.empty else None,
                    'end': max(df['date']).isoformat() if not df.empty else None
                }
            }
            
        except Exception as e:
            logger.error(f"Sentiment trend analysis error: {str(e)}")
            return {'trends': [], 'error': str(e)}
