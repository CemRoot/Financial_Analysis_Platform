# backend/scripts/data_collection/fetch_training_data.py

import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financial_analysis.settings")
django.setup()

# Import Django models and services
from django.conf import settings
from apps.stocks.models import Stock, StockPrice
from apps.news.models import NewsArticle, NewsSource
from apps.stocks.services.stock_service import StockDataService
from apps.news.services.news_service import NewsAPIService
from apps.news.sentiment.google_sentiment import GoogleNLPSentiment

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrainingDataCollector:
    """
    Collects and prepares data for training ML models
    """
    
    def __init__(self, days_back=90):
        """
        Initialize the collector
        
        days_back: Number of days to look back for historical data
        """
        self.days_back = days_back
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=days_back)
        self.stock_symbols = settings.DATA_COLLECTION['STOCK_SYMBOLS']
        self.sentiment_analyzer = GoogleNLPSentiment()
        
    def collect_stock_data(self):
        """
        Collect historical stock data
        """
        logger.info(f"Collecting stock data for {len(self.stock_symbols)} symbols from {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        
        all_stock_data = []
        
        for symbol in self.stock_symbols:
            try:
                logger.info(f"Fetching data for {symbol}")
                
                # Get stock info
                stock_info = StockDataService.get_stock_info(symbol)
                if not stock_info:
                    logger.warning(f"Could not get info for {symbol}")
                    continue
                
                # Save to database
                stock, created = Stock.objects.update_or_create(
                    symbol=symbol,
                    defaults={
                        'company_name': stock_info['name'],
                        'sector': stock_info['sector'],
                        'industry': stock_info['industry'],
                        'market_cap': stock_info['market_cap'],
                        'website': stock_info['website'],
                        'logo_url': stock_info['logo_url']
                    }
                )
                
                # Get historical data
                historical_data = StockDataService.get_historical_data(
                    symbol, 
                    period=f"{self.days_back}d", 
                    interval="1d"
                )
                
                # Process and store data
                stock_prices = []
                for data_point in historical_data:
                    date_str = data_point['date']
                    
                    # Skip if date is not provided
                    if not date_str:
                        continue
                    
                    # Parse date
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    # Skip if out of range
                    if date_obj < self.start_date.date() or date_obj > self.end_date.date():
                        continue
                    
                    # Calculate price change and direction
                    price_change = 0
                    direction = 0  # 0: no change, 1: up, -1: down
                    
                    if len(stock_prices) > 0:
                        prev_close = stock_prices[-1]['close']
                        curr_close = data_point['close']
                        price_change = ((curr_close - prev_close) / prev_close) * 100
                        direction = 1 if price_change > 0 else (-1 if price_change < 0 else 0)
                    
                    # Add processed data point
                    stock_prices.append({
                        'symbol': symbol,
                        'date': date_obj,
                        'open': data_point['open'],
                        'high': data_point['high'],
                        'low': data_point['low'],
                        'close': data_point['close'],
                        'volume': data_point['volume'],
                        'price_change': price_change,
                        'direction': direction
                    })
                    
                    # Save to database
                    StockPrice.objects.update_or_create(
                        stock=stock,
                        date=date_obj,
                        defaults={
                            'open_price': data_point['open'],
                            'high_price': data_point['high'],
                            'low_price': data_point['low'],
                            'close_price': data_point['close'],
                            'adjusted_close': data_point['close'],
                            'volume': data_point['volume']
                        }
                    )
                
                all_stock_data.extend(stock_prices)
                
                # Sleep to avoid hitting API rate limits
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {str(e)}")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_stock_data)
        
        # Save to CSV
        os.makedirs('data', exist_ok=True)
        csv_path = 'data/stock_data.csv'
        df.to_csv(csv_path, index=False)
        
        logger.info(f"Collected {len(df)} stock price records, saved to {csv_path}")
        
        return df
    
    def collect_news_data(self):
        """
        Collect news articles for the specified period
        """
        logger.info(f"Collecting news articles from {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        
        all_news_data = []
        
        # Collect news for each stock
        for symbol in self.stock_symbols:
            try:
                logger.info(f"Fetching news for {symbol}")
                
                # Get stock object
                try:
                    stock = Stock.objects.get(symbol=symbol)
                except Stock.DoesNotExist:
                    logger.warning(f"Stock {symbol} not found in database")
                    continue
                
                # Get company news
                company_news = NewsAPIService.get_company_news(
                    company_symbol=symbol,
                    company_name=stock.company_name,
                    days=self.days_back
                )
                
                if not company_news:
                    logger.warning(f"No news found for {symbol}")
                    continue
                
                # Process news articles
                for article in company_news['articles']:
                    try:
                        # Skip if no title or no publication date
                        if not article['title'] or not article['published_at']:
                            continue
                        
                        # Parse publication date
                        pub_date = datetime.strptime(article['published_at'], "%Y-%m-%dT%H:%M:%SZ")
                        
                        # Skip if out of range
                        if pub_date < self.start_date or pub_date > self.end_date:
                            continue
                        
                        # Get or create news source
                        source, _ = NewsSource.objects.get_or_create(
                            name=article['source'],
                            defaults={'url': ''}
                        )
                        
                        # Analyze sentiment with Google NLP
                        sentiment_data = None
                        if self.sentiment_analyzer.client:
                            sentiment_data = self.sentiment_analyzer.analyze_sentiment(article['title'])
                        
                        # Create sentiment label
                        sentiment_label = 'neutral'
                        sentiment_score = 0
                        
                        if sentiment_data:
                            sentiment_score = sentiment_data['score']
                            sentiment_label = 'positive' if sentiment_score > 0.2 else (
                                'negative' if sentiment_score < -0.2 else 'neutral'
                            )
                        
                        # Save to database
                        news_article, created = NewsArticle.objects.update_or_create(
                            url=article['url'],
                            defaults={
                                'title': article['title'],
                                'content': article['content'] or "",
                                'summary': article['description'] or "",
                                'image_url': article['image_url'] or "",
                                'published_at': pub_date,
                                'source': source,
                                'sentiment_score': sentiment_score,
                                'is_positive': sentiment_label == 'positive',
                                'is_negative': sentiment_label == 'negative',
                                'is_neutral': sentiment_label == 'neutral'
                            }
                        )
                        
                        # Link to the stock
                        news_article.stocks.add(stock)
                        
                        # Find the next day's price change
                        next_day = pub_date.date() + timedelta(days=1)
                        
                        # Look for the next trading day
                        while True:
                            # Try to find next day's price
                            try:
                                next_price = StockPrice.objects.get(
                                    stock=stock,
                                    date=next_day
                                )
                                break
                            except StockPrice.DoesNotExist:
                                # Try the next calendar day
                                next_day += timedelta(days=1)
                                
                                # Stop if we're past the end date
                                if next_day > self.end_date.date():
                                    next_price = None
                                    break
                        
                        # Get the current day's price
                        try:
                            current_price = StockPrice.objects.get(
                                stock=stock,
                                date=pub_date.date()
                            )
                        except StockPrice.DoesNotExist:
                            # Look for the most recent prior price
                            current_price = StockPrice.objects.filter(
                                stock=stock,
                                date__lt=pub_date.date()
                            ).order_by('-date').first()
                        
                        # Calculate market movement
                        market_movement = 0  # 0: no change, 1: up, -1: down
                        price_change = 0
                        
                        if current_price and next_price:
                            price_change = ((next_price.close_price - current_price.close_price) / 
                                          current_price.close_price) * 100
                            market_movement = 1 if price_change > 0 else (-1 if price_change < 0 else 0)
                        
                        # Add to news data
                        all_news_data.append({
                            'symbol': symbol,
                            'title': article['title'],
                            'description': article['description'],
                            'published_at': pub_date,
                            'source': article['source'],
                            'sentiment_score': sentiment_score,
                            'sentiment_label': sentiment_label,
                            'next_day_price_change': price_change,
                            'market_movement': market_movement
                        })
                    
                    except Exception as e:
                        logger.error(f"Error processing news article: {str(e)}")
                
                # Sleep to avoid hitting API rate limits
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting news for {symbol}: {str(e)}")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_news_data)
        
        # Save to CSV
        os.makedirs('data', exist_ok=True)
        csv_path = 'data/news_data.csv'
        df.to_csv(csv_path, index=False)
        
        logger.info(f"Collected {len(df)} news articles, saved to {csv_path}")
        
        return df
    
    def create_training_dataset(self):
        """
        Combine stock and news data to create a dataset for ML training
        """
        logger.info("Creating training dataset...")
        
        # Collect data
        stock_data = self.collect_stock_data()
        news_data = self.collect_news_data()
        
        # Check if we have data
        if stock_data.empty or news_data.empty:
            logger.error("No data collected, cannot create training dataset")
            return None
        
        # Save combined dataset
        os.makedirs('data', exist_ok=True)
        csv_path = 'data/training_data.csv'
        news_data.to_csv(csv_path, index=False)
        
        logger.info(f"Created training dataset with {len(news_data)} samples, saved to {csv_path}")
        
        return news_data

# Run the collector if script is executed directly
if __name__ == "__main__":
    collector = TrainingDataCollector(days_back=90)
    training_data = collector.create_training_dataset()
    
    if training_data is not None:
        logger.info(f"Dataset summary:")
        logger.info(f"Samples: {len(training_data)}")
        logger.info(f"Positive samples: {sum(training_data['sentiment_label'] == 'positive')}")
        logger.info(f"Neutral samples: {sum(training_data['sentiment_label'] == 'neutral')}")
        logger.info(f"Negative samples: {sum(training_data['sentiment_label'] == 'negative')}")
        logger.info(f"Up movements: {sum(training_data['market_movement'] == 1)}")
        logger.info(f"Down movements: {sum(training_data['market_movement'] == -1)}")
        logger.info(f"No movements: {sum(training_data['market_movement'] == 0)}")