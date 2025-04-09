from django.db import models
from django.utils import timezone
from apps.stocks.models import Stock

class NewsSource(models.Model):
    """
    Model to store news sources/publishers
    """
    name = models.CharField(max_length=100)
    url = models.URLField()
    logo_url = models.URLField(blank=True, null=True)
    reliability_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class NewsCategory(models.Model):
    """
    Model to categorize news articles
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "News Categories"
    
    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    """
    Model to store financial news articles
    """
    title = models.CharField(max_length=255)
    summary = models.TextField()
    content = models.TextField()
    url = models.URLField(unique=True)
    published_date = models.DateTimeField()
    image_url = models.URLField(blank=True, null=True)
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    stocks = models.ManyToManyField(Stock, related_name='news_articles', blank=True)
    
    # Sentiment analysis
    sentiment_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)  # -1.0 to 1.0
    
    # Additional metadata
    author = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['sentiment_score']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_recent(self):
        """Return True if the article is less than 24 hours old."""
        return (timezone.now() - self.published_date).days < 1
