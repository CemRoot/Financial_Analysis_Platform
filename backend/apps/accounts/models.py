# backend/apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser to add additional fields
    """
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # User preferences for dashboard
    dark_mode = models.BooleanField(default=False)
    notification_enabled = models.BooleanField(default=True)
    
    # Login tracking
    last_activity = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)
    
    # Required by Django for the custom user model
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def update_last_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def record_login(self):
        """Record a login event"""
        self.login_count += 1
        self.save(update_fields=['login_count'])

class Watchlist(models.Model):
    """
    Model to store user's favorite stocks as a watchlist
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s watchlist: {self.name}"

class WatchlistItem(models.Model):
    """
    Individual stock items in a user's watchlist
    """
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='items')
    symbol = models.CharField(max_length=10)  # Stock symbol/ticker
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('watchlist', 'symbol')
    
    def __str__(self):
        return f"{self.symbol} in {self.watchlist.name}"

class UserPreference(models.Model):
    """
    Additional user preferences like news categories and notification settings
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    preferred_news_categories = models.JSONField(default=list)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    price_alert_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)  # Default 5% change
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

class UserActivity(models.Model):
    """
    Model to track user activity and interactions with the platform
    """
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view_stock', 'View Stock'),
        ('view_news', 'View News'),
        ('add_to_watchlist', 'Add to Watchlist'),
        ('remove_from_watchlist', 'Remove from Watchlist'),
        ('search', 'Search'),
        ('create_alert', 'Create Alert'),
        ('view_prediction', 'View Prediction'),
        ('dashboard_interaction', 'Dashboard Interaction'),
        ('settings_changed', 'Settings Changed'),
        ('other', 'Other')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Details of the activity (e.g., stock symbol, search query, etc.)
    details = models.JSONField(default=dict, blank=True)
    
    # IP address and user agent information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=40, blank=True)
    
    # Related object ID and type (e.g., a stock, news article, etc.)
    object_id = models.CharField(max_length=50, blank=True)
    content_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name_plural = "User activities"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}"

class StockInteraction(models.Model):
    """
    Detailed tracking of user interactions with specific stocks
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='stock_interactions')
    symbol = models.CharField(max_length=10)
    
    # Counts of different types of interactions
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    search_count = models.IntegerField(default=0)
    last_searched = models.DateTimeField(null=True, blank=True)
    
    # Time spent viewing this stock (in seconds)
    total_view_time = models.IntegerField(default=0)
    
    # Whether this stock is a favorite
    is_favorite = models.BooleanField(default=False)
    
    # Custom notes about this stock
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('user', 'symbol')
    
    def __str__(self):
        return f"{self.user.username}'s interaction with {self.symbol}"
    
    def record_view(self):
        """Record a stock view interaction"""
        self.view_count += 1
        self.last_viewed = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed'])
    
    def record_search(self):
        """Record a stock search interaction"""
        self.search_count += 1
        self.last_searched = timezone.now()
        self.save(update_fields=['search_count', 'last_searched'])
