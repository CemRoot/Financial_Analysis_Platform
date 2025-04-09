# backend/apps/predictions/data_processors/news_processor.py

import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import logging

logger = logging.getLogger(__name__)

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class NewsProcessor:
    """
    Processes news headlines and articles for sentiment analysis and prediction models
    """
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Add finance-specific stopwords
        self.stop_words.update(['says', 'report', 'reported', 'quarter', 'quarterly'])
        
    def preprocess_text(self, text):
        """
        Clean and preprocess text
        """
        if not text or not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        tokens = [t for t in tokens if t not in self.stop_words]
        
        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
        
        return ' '.join(tokens)
    
    def extract_features(self, text, return_count_vector=False):
        """
        Extract features from text for sentiment analysis
        """
        # Feature extraction methods could include:
        # - Count of positive/negative finance terms
        # - Presence of specific keywords
        # - Text statistics (length, word count, etc.)
        
        features = {}
        
        # Simple text statistics
        features['text_length'] = len(text)
        features['word_count'] = len(text.split())
        
        # Finance-specific keyword presence
        pos_keywords = ['rise', 'gain', 'profit', 'growth', 'up', 'higher', 'bull', 'positive']
        neg_keywords = ['drop', 'fall', 'loss', 'decline', 'down', 'lower', 'bear', 'negative']
        
        features['positive_count'] = sum(1 for word in text.split() if word in pos_keywords)
        features['negative_count'] = sum(1 for word in text.split() if word in neg_keywords)
        features['sentiment_ratio'] = features['positive_count'] / (features['negative_count'] + 1)  # +1 to avoid division by zero
        
        if return_count_vector:
            # Convert features to a single vector
            return np.array([
                features['text_length'],
                features['word_count'],
                features['positive_count'],
                features['negative_count'],
                features['sentiment_ratio']
            ])
        
        return features
    
    def process_headlines(self, headlines):
        """
        Process a list of news headlines
        """
        processed_headlines = []
        features = []
        
        for headline in headlines:
            processed_text = self.preprocess_text(headline)
            headline_features = self.extract_features(processed_text)
            
            processed_headlines.append(processed_text)
            features.append(headline_features)
        
        return {
            'processed_headlines': processed_headlines,
            'features': features
        }
    
    def create_training_dataset(self, headlines, market_movements):
        """
        Create a dataset for training prediction models
        
        - headlines: List of news headlines
        - market_movements: Binary (0/1) list indicating market direction (up/down)
        """
        if len(headlines) != len(market_movements):
            raise ValueError("Headlines and market movements must have the same length")
            
        processed_data = self.process_headlines(headlines)
        processed_headlines = processed_data['processed_headlines']
        
        # Create DataFrame
        df = pd.DataFrame({
            'headline': headlines,
            'processed_headline': processed_headlines,
            'market_movement': market_movements
        })
        
        # Add features
        for idx, feature_dict in enumerate(processed_data['features']):
            for key, value in feature_dict.items():
                df.loc[idx, key] = value
        
        return df
        
    def preprocess_news_texts(self, news_texts):
        """
        Process a list of news texts including headlines and content
        """
        if not news_texts:
            return []
            
        processed_texts = []
        for text in news_texts:
            processed_text = self.preprocess_text(text)
            processed_texts.append(processed_text)
            
        return processed_texts