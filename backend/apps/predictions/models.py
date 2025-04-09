# backend/apps/predictions/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.stocks.models import Stock
from apps.accounts.models import CustomUser

class ForecastModel(models.Model):
    """
    Model to store different forecasting models
    """
    MODEL_TYPES = [
        ('logistic_regression', 'Logistic Regression'),
        ('random_forest', 'Random Forest'),
        ('lstm', 'LSTM Neural Network'),
        ('bert', 'BERT'),
        ('bert_lstm', 'Hybrid BERT-LSTM'),
        ('ensemble', 'Ensemble Model'),
    ]
    
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict)  # Store model parameters
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.model_type})"

class StockPrediction(models.Model):
    """
    Model to store stock price predictions
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='predictions')
    forecast_model = models.ForeignKey(ForecastModel, on_delete=models.CASCADE, related_name='predictions')
    prediction_date = models.DateField()  # Date when prediction was made
    target_date = models.DateField()  # Date for which price is predicted
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    lower_bound = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    upper_bound = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                    validators=[MinValueValidator(0), MaxValueValidator(100)])
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    error_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('stock', 'forecast_model', 'prediction_date', 'target_date')
        indexes = [
            models.Index(fields=['stock', 'target_date']),
            models.Index(fields=['prediction_date']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - predicted {self.predicted_price} for {self.target_date}"

class PredictionMetrics(models.Model):
    """
    Model to store performance metrics for prediction models
    """
    forecast_model = models.ForeignKey(ForecastModel, on_delete=models.CASCADE, related_name='metrics')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prediction_metrics')
    evaluation_date = models.DateField()
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    precision = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    recall = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    f1_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    mae = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Mean Absolute Error
    mse = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Mean Squared Error
    rmse = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Root Mean Squared Error
    additional_metrics = models.JSONField(default=dict, blank=True)  # For additional metrics
    
    class Meta:
        unique_together = ('forecast_model', 'stock', 'evaluation_date')
        verbose_name_plural = "Prediction Metrics"
    
    def __str__(self):
        return f"{self.forecast_model.name} metrics for {self.stock.symbol} on {self.evaluation_date}"