# backend/apps/stocks/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.accounts.models import CustomUser

class Stock(models.Model):
    """
    Temel hisse senedi bilgilerini tutan model
    """
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    exchange = models.CharField(max_length=50, null=True, blank=True)
    logo_url = models.URLField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    class Meta:
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['sector']),
        ]

class StockPrice(models.Model):
    """
    Hisse senedi fiyat verilerini tutan model
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    open = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    adjusted_close = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField()
    
    class Meta:
        unique_together = ('stock', 'date')
        indexes = [
            models.Index(fields=['stock', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.date} - {self.close}"

class StockFinancial(models.Model):
    """
    Hisse senedi finansal verilerini tutan model (çeyreklik/yıllık)
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='financials')
    period = models.CharField(max_length=10)  # 'Q1', 'Q2', 'Q3', 'Q4', 'Annual'
    year = models.IntegerField()
    date = models.DateField()
    
    # Finansal metrikler
    revenue = models.BigIntegerField(null=True, blank=True)
    gross_profit = models.BigIntegerField(null=True, blank=True)
    operating_income = models.BigIntegerField(null=True, blank=True)
    net_income = models.BigIntegerField(null=True, blank=True)
    eps = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    peg_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('stock', 'period', 'year')
        indexes = [
            models.Index(fields=['stock', 'date']),
            models.Index(fields=['year', 'period']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.period} {self.year}"

class TechnicalIndicator(models.Model):
    """
    Hisse senetleri için teknik göstergeleri tutan model
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='indicators')
    date = models.DateField()
    
    # Temel göstergeler
    sma_20 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sma_50 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sma_200 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ema_12 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ema_26 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    macd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    macd_signal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    macd_histogram = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rsi_14 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stoch_k = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stoch_d = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    bollinger_upper = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bollinger_middle = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bollinger_lower = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # İlave göstergeler alanları eklenebilir
    additional_indicators = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ('stock', 'date')
        indexes = [
            models.Index(fields=['stock', 'date']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"

class StockAlert(models.Model):
    """
    Kullanıcıların belirli hisse senetleri için kurdukları alarmlar
    """
    ALERT_TYPES = [
        ('price_above', 'Price Above'),
        ('price_below', 'Price Below'),
        ('percent_change', 'Percent Change'),
        ('volume_spike', 'Volume Spike'),
        ('rsi_above', 'RSI Above'),
        ('rsi_below', 'RSI Below'),
        ('sma_cross_above', 'SMA Cross Above'),
        ('sma_cross_below', 'SMA Cross Below'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('triggered', 'Triggered'),
        ('disabled', 'Disabled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='stock_alerts')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    
    # Bildirim tercihleri
    notify_email = models.BooleanField(default=True)
    notify_browser = models.BooleanField(default=True)
    
    # Ek veriler
    additional_parameters = models.JSONField(default=dict, blank=True)  # Ör: SMA periyodu
    
    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol} - {self.alert_type} - {self.value}"

class MarketIndex(models.Model):
    """
    S&P 500, NASDAQ, Dow Jones gibi piyasa endekslerini tutan model
    """
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

class IndexPrice(models.Model):
    """
    Piyasa endeksleri için fiyat verilerini tutan model
    """
    index = models.ForeignKey(MarketIndex, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    open = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ('index', 'date')
        indexes = [
            models.Index(fields=['index', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.index.symbol} - {self.date} - {self.close}"
