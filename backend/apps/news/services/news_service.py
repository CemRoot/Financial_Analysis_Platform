# backend/apps/news/services/news_service.py

import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

class NewsService:
    """
    News API.ai integration for financial news
    """
    
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY or '5ce5519c-39ba-4e15-a1e7-53ad1711a737'  # Use from settings or the provided key
        self.api_url = "https://api.newsapi.ai"
        
        # Validate API key exists during initialization
        if not self.api_key:
            logger.critical("NEWS_API_KEY is not set in settings or is empty. News API will not function!")
    
    def get_general_financial_news(self, page=1, page_size=20):
        """
        Get general financial news using NewsAPI.ai
        """
        try:
            # Validate API key before making request
            if not self.api_key:
                return {"error": "News API key is not configured", "status_code": 500}
            
            # Current date and one week ago
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            # NewsAPI.ai article search endpoint
            url = f"{self.api_url}/articleSearch"
            
            params = {
                "apiKey": self.api_key,
                "keyword": "finance OR economy OR market OR stock",
                "keywordLoc": "title,body",
                "startSourceRankPercentile": 0,
                "endSourceRankPercentile": 100,
                "articlesSortBy": "date",
                "articlesSortByAsc": False,
                "articlesCount": page_size,
                "articlesPage": page,
                "includeArticleCategories": True,
                "includeArticleImage": True,
                "includeArticleVideos": False,
                "includeArticleLinks": False,
                "startDate": start_date,
                "endDate": end_date,
                "dataType": ["news"],
                "resultType": "articles",
                "forceMaxDataTimeWindow": 31
            }
            
            logger.info(f"Fetching financial news from {url}")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return self._format_news_response(response.json())
            elif response.status_code == 401:
                logger.critical(f"News API authentication failed: Invalid API key or unauthorized access")
                return {"error": "News API authentication failed. Please check API key configuration.", "status_code": 401}
            else:
                logger.error(f"News API error: {response.status_code} - {response.text}")
                return {"error": f"Failed to fetch news: {response.status_code}", "status_code": response.status_code}
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to News API: {str(e)}")
            return {"error": "Could not connect to News API. Please check your network connection.", "status_code": 503}
        except Exception as e:
            logger.error(f"Error fetching general financial news: {str(e)}")
            return {"error": f"Failed to fetch news: {str(e)}", "status_code": 500}
    
    def get_stock_specific_news(self, symbol, days_back=7, page=1, page_size=20):
        """
        Get news specifically about a stock symbol using NewsAPI.ai
        """
        try:
            # Set date range
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            # NewsAPI.ai article search endpoint
            url = f"{self.api_url}/articleSearch"
            
            # If symbol is a company like AAPL, get the company name for better search
            company_name = self._get_company_name(symbol)
            search_query = f"{symbol} OR {company_name}" if company_name else symbol
            
            params = {
                "apiKey": self.api_key,
                "keyword": f"({search_query}) AND (stock OR share OR market OR investment OR earnings OR finance)",
                "keywordLoc": "title,body",
                "startSourceRankPercentile": 0,
                "endSourceRankPercentile": 100,
                "articlesSortBy": "date",
                "articlesSortByAsc": False,
                "articlesCount": page_size,
                "articlesPage": page,
                "includeArticleCategories": True,
                "includeArticleImage": True,
                "includeArticleVideos": False,
                "includeArticleLinks": False,
                "startDate": start_date,
                "endDate": end_date,
                "categoryUri": "news/Business",
                "dataType": ["news"],
                "resultType": "articles",
                "forceMaxDataTimeWindow": 31
            }
            
            logger.info(f"Fetching news for {symbol} from {url}")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return self._format_news_response(response.json())
            else:
                logger.error(f"News API error for {symbol}: {response.status_code} - {response.text}")
                return {"error": f"Failed to fetch news for {symbol}: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return {"error": f"Failed to fetch news for {symbol}: {str(e)}"}
    
    def search_news(self, query, from_date=None, to_date=None, page=1, page_size=20):
        """
        Search news with a custom query using NewsAPI.ai
        """
        try:
            # Set default date range if not provided
            end_date = to_date or datetime.now().strftime("%Y-%m-%d")
            start_date = from_date or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # NewsAPI.ai article search endpoint
            url = f"{self.api_url}/articleSearch"
            
            params = {
                "apiKey": self.api_key,
                "keyword": query,
                "keywordLoc": "title,body",
                "startSourceRankPercentile": 0,
                "endSourceRankPercentile": 100,
                "articlesSortBy": "date",
                "articlesSortByAsc": False,
                "articlesCount": page_size,
                "articlesPage": page,
                "includeArticleCategories": True,
                "includeArticleImage": True,
                "includeArticleVideos": False,
                "includeArticleLinks": False,
                "startDate": start_date,
                "endDate": end_date,
                "dataType": ["news"],
                "resultType": "articles",
                "forceMaxDataTimeWindow": 31
            }
            
            logger.info(f"Searching news for '{query}' from {url}")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return self._format_news_response(response.json())
            else:
                logger.error(f"News API search error: {response.status_code} - {response.text}")
                return {"error": f"Failed to search news: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error searching news: {str(e)}")
            return {"error": f"Failed to search news: {str(e)}"}
    
    def get_sentiment_analysis(self, symbol, days_back=30):
        """
        Get sentiment analysis for a stock symbol using NewsAPI.ai
        """
        try:
            # Set date range
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            # NewsAPI.ai article search endpoint with sentiment analysis
            url = f"{self.api_url}/articleSearch"
            
            # If symbol is a company like AAPL, get the company name for better search
            company_name = self._get_company_name(symbol)
            search_query = f"{symbol} OR {company_name}" if company_name else symbol
            
            params = {
                "apiKey": self.api_key,
                "keyword": f"({search_query}) AND (stock OR share OR market OR investment OR earnings OR finance)",
                "keywordLoc": "title,body",
                "startSourceRankPercentile": 0,
                "endSourceRankPercentile": 100,
                "articlesSortBy": "date",
                "articlesSortByAsc": False,
                "articlesCount": 100,  # Get more articles for better sentiment analysis
                "includeArticleCategories": True,
                "includeArticleImage": False,
                "includeArticleVideos": False,
                "includeArticleLinks": False,
                "includeSourceRankInfo": True,
                "includeSourceInfo": True,
                "includeSentiment": True,  # Request sentiment analysis
                "startDate": start_date,
                "endDate": end_date,
                "categoryUri": "news/Business",
                "dataType": ["news"],
                "resultType": "articles",
                "forceMaxDataTimeWindow": 31
            }
            
            logger.info(f"Fetching sentiment analysis for {symbol} from {url}")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return self._format_sentiment_response(response.json(), symbol)
            else:
                logger.error(f"News API sentiment error for {symbol}: {response.status_code} - {response.text}")
                return {"error": f"Failed to fetch sentiment for {symbol}: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error fetching sentiment for {symbol}: {str(e)}")
            return {"error": f"Failed to fetch sentiment for {symbol}: {str(e)}"}
    
    def _format_news_response(self, api_response):
        """
        Format the NewsAPI.ai response to our standard format
        """
        if not api_response or 'articles' not in api_response:
            return {
                'articles': [],
                'total_results': 0,
                'status': 'error'
            }
            
        articles_data = api_response.get('articles', {}).get('results', [])
        total_count = api_response.get('articles', {}).get('totalResults', 0)
        
        formatted_articles = []
        for article in articles_data:
            # Get the best available image
            image_url = ""
            if article.get('image'):
                image_url = article['image']
            elif article.get('links') and article['links'].get('thumbnail'):
                image_url = article['links']['thumbnail']
            
            # Extract and format date
            published_date = article.get('date', '')
            if published_date:
                try:
                    # Convert to readable format if it's a timestamp
                    date_obj = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    published_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    pass
            
            formatted_articles.append({
                'title': article.get('title', ''),
                'description': article.get('body', '')[:300] + '...' if len(article.get('body', '')) > 300 else article.get('body', ''),
                'content': article.get('body', ''),
                'url': article.get('url', ''),
                'image_url': image_url,
                'source': article.get('source', {}).get('title', ''),
                'published_at': published_date,
                'author': article.get('author', ''),
                'sentiment': article.get('sentiment', {})
            })
        
        return {
            'articles': formatted_articles,
            'total_results': total_count,
            'status': 'ok'
        }
    
    def _format_sentiment_response(self, api_response, symbol):
        """
        Format the sentiment analysis response
        """
        if not api_response or 'articles' not in api_response:
            return {
                'sentiment_data': [],
                'average_sentiment': 0,
                'total_articles': 0,
                'status': 'error'
            }
            
        articles_data = api_response.get('articles', {}).get('results', [])
        total_count = len(articles_data)
        
        if total_count == 0:
            return {
                'sentiment_data': [],
                'average_sentiment': 0,
                'total_articles': 0,
                'status': 'ok'
            }
        
        # Process sentiment data and group by date
        sentiment_by_date = {}
        total_sentiment = 0
        articles_with_sentiment = 0
        
        for article in articles_data:
            if 'sentiment' not in article:
                continue
                
            sentiment = article.get('sentiment', {})
            sentiment_value = sentiment.get('sentiment', 0)
            
            # Skip if no sentiment data
            if sentiment_value is None:
                continue
                
            # Format date for grouping (just the date part)
            date_str = article.get('date', '')[:10]  # YYYY-MM-DD format
            
            if date_str not in sentiment_by_date:
                sentiment_by_date[date_str] = {
                    'date': date_str,
                    'total_sentiment': 0,
                    'article_count': 0,
                    'average_sentiment': 0
                }
            
            # Add sentiment data
            sentiment_by_date[date_str]['total_sentiment'] += sentiment_value
            sentiment_by_date[date_str]['article_count'] += 1
            
            # Update totals
            total_sentiment += sentiment_value
            articles_with_sentiment += 1
        
        # Calculate averages for each date
        sentiment_data = []
        for date, data in sentiment_by_date.items():
            if data['article_count'] > 0:
                data['average_sentiment'] = round(data['total_sentiment'] / data['article_count'], 2)
            sentiment_data.append(data)
        
        # Sort by date
        sentiment_data.sort(key=lambda x: x['date'])
        
        # Calculate overall average
        average_sentiment = 0
        if articles_with_sentiment > 0:
            average_sentiment = round(total_sentiment / articles_with_sentiment, 2)
        
        return {
            'symbol': symbol,
            'sentiment_data': sentiment_data,
            'average_sentiment': average_sentiment,
            'total_articles': articles_with_sentiment,
            'status': 'ok'
        }
    
    def _get_company_name(self, symbol):
        """
        Get company name for a stock symbol to improve search results
        """
        # Common stock symbols and their company names
        stock_names = {
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'AMZN': 'Amazon',
            'GOOGL': 'Google',
            'GOOG': 'Google',
            'META': 'Facebook',
            'TSLA': 'Tesla',
            'NVDA': 'NVIDIA',
            'JPM': 'JPMorgan',
            'V': 'Visa',
            'BAC': 'Bank of America',
            'DIS': 'Disney',
            'NFLX': 'Netflix',
            'CSCO': 'Cisco',
            'INTC': 'Intel',
            'XOM': 'Exxon Mobil',
            'KO': 'Coca-Cola',
            'PEP': 'PepsiCo',
            'WMT': 'Walmart',
            'PG': 'Procter & Gamble',
            'JNJ': 'Johnson & Johnson'
        }
        
        return stock_names.get(symbol, '')
