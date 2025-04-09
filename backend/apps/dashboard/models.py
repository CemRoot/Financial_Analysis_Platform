from django.db import models
from apps.accounts.models import CustomUser

class DashboardWidget(models.Model):
    """
    Model to store different types of dashboard widgets
    """
    WIDGET_TYPES = [
        ('stock_chart', 'Stock Chart'),
        ('market_overview', 'Market Overview'),
        ('news_feed', 'News Feed'),
        ('watchlist', 'Watchlist'),
        ('performance', 'Portfolio Performance'),
        ('prediction', 'Stock Predictions'),
        ('custom', 'Custom Widget'),
    ]
    
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon class or name
    is_default = models.BooleanField(default=False)
    
    # Default configuration for this widget type
    default_config = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"

class UserDashboardWidget(models.Model):
    """
    Model linking widgets to users with customization options
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)  # Order of widgets on dashboard
    size = models.CharField(max_length=20, default='medium')  # small, medium, large
    is_enabled = models.BooleanField(default=True)
    
    # User-specific configuration that overrides default
    config = models.JSONField(default=dict)
    
    # Last time this widget was refreshed
    last_refreshed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'widget')
        ordering = ['position']
    
    def __str__(self):
        return f"{self.user.username}'s {self.widget.name} widget"
    
    def get_config(self):
        """Merge default config with user config, with user config taking precedence"""
        result = self.widget.default_config.copy()
        result.update(self.config)
        return result
