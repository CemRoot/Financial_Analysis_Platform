# backend/scripts/ml_scripts/train_models.py

import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financial_analysis.settings")
django.setup()

# Import Django models
from django.conf import settings
from apps.stocks.models import Stock
from apps.predictions.models import ForecastModel, PredictionMetrics
from apps.predictions.ml_models.traditional_models import MarketDirectionPredictor
from apps.predictions.ml_models.deep_learning import LSTMNewsModel, BERTNewsModel
from apps.predictions.ml_models.hybrid_models import BERTLSTMHybridModel
from apps.predictions.ml_models.model_evaluation import ModelEvaluator
from apps.predictions.data_processors.news_processor import NewsDataProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model_training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """
    Trains and evaluates ML models for financial news sentiment analysis and market prediction
    """
    
    def __init__(self, data_path=None, test_size=0.2, random_state=42):
        """
        Initialize the trainer
        
        data_path: Path to the training data CSV
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        """
        self.data_path = data_path or 'data/training_data.csv'
        self.test_size = test_size
        self.random_state = random_state
        self.news_processor = NewsDataProcessor()
        self.models_dir = settings.ML_MODELS_DIR
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
    
    def load_and_prepare_data(self):
        """
        Load and prepare data for training
        """
        logger.info(f"Loading data from {self.data_path}")
        
        # Check if file exists
        if not os.path.exists(self.data_path):
            logger.error(f"Data file not found: {self.data_path}")
            return None
        
        # Load data
        df = pd.read_csv(self.data_path)
        
        logger.info(f"Loaded {len(df)} samples")
        
        # Basic data cleaning
        df = df.dropna(subset=['title', 'market_movement'])
        
        # Preprocess text
        df['processed_title'] = df['title'].apply(self.news_processor.preprocess_text)
        
        # Filter out rows with empty processed text
        df = df[df['processed_title'].str.strip() != '']
        
        logger.info(f"After cleaning: {len(df)} samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df['processed_title'],
            df['market_movement'].apply(lambda x: 1 if x > 0 else 0),  # Binary classification: up (1) or not up (0)
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=df['market_movement'].apply(lambda x: 1 if x > 0 else 0)
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'full_data': df
        }
    
    def train_and_evaluate(self):
        """
        Train and evaluate all models
        """
        # Load data
        data = self.load_and_prepare_data()
        if data is None:
            return
        
        X_train, X_test = data['X_train'], data['X_test']
        y_train, y_test = data['y_train'], data['y_test']
        
        # Create evaluator
        evaluator = ModelEvaluator()
        
        # Train and evaluate traditional models
        logger.info("Training Logistic Regression model...")
        lr_model = MarketDirectionPredictor(model_type='logistic_regression')
        lr_model.train(X_train, y_train)
        evaluator.add_model('LogisticRegression', lr_model)
        
        # Save model
        with open(os.path.join(self.models_dir, 'logistic_regression.pkl'), 'wb') as f:
            pickle.dump(lr_model, f)
        
        logger.info("Training Random Forest model...")
        rf_model = MarketDirectionPredictor(model_type='random_forest')
        rf_model.train(X_train, y_train)
        evaluator.add_model('RandomForest', rf_model)
        
        # Save model
        with open(os.path.join(self.models_dir, 'random_forest.pkl'), 'wb') as f:
            pickle.dump(rf_model, f)
        
        # Evaluate all models
        logger.info("Evaluating models...")
        results = evaluator.evaluate_all(X_test, y_test)
        
        # Display results
        summary_df = evaluator.get_summary_dataframe()
        logger.info("\nModel Performance Summary:")
        logger.info(summary_df)
        
        # Save evaluation results
        summary_df.to_csv(os.path.join(self.models_dir, 'model_evaluation.csv'))
        
        # Create confusion matrices
        logger.info("Generating confusion matrices...")
        confusion_fig = evaluator.plot_confusion_matrices(y_test)
        confusion_fig.savefig(os.path.join(self.models_dir, 'confusion_matrices.png'))
        
        # Plot ROC curves
        logger.info("Generating ROC curves...")
        roc_fig = evaluator.plot_roc_curves(X_test, y_test)
        roc_fig.savefig(os.path.join(self.models_dir, 'roc_curves.png'))
        
        # Plot execution times
        logger.info("Generating execution time comparison...")
        time_fig = evaluator.plot_execution_times()
        time_fig.savefig(os.path.join(self.models_dir, 'execution_times.png'))
        
        # Store results in database
        for model_name, metrics in results.items():
            # Get or create the model in database
            model_type = model_name.lower()
            if model_name == 'LogisticRegression':
                model_type = 'logistic_regression'
            elif model_name == 'RandomForest':
                model_type = 'random_forest'
            
            forecast_model, created = ForecastModel.objects.update_or_create(
                name=model_name,
                defaults={
                    'model_type': model_type,
                    'description': f'Trained on {len(X_train)} news headlines',
                    'parameters': {
                        'random_state': self.random_state,
                        'test_size': self.test_size
                    },
                    'is_active': True
                }
            )
            
            if created:
                logger.info(f"Created new model record: {model_name}")
            else:
                logger.info(f"Updated existing model record: {model_name}")
            
            # Add metrics for stock market (general)
            stock, _ = Stock.objects.get_or_create(
                symbol='MARKET',
                defaults={'company_name': 'Overall Market', 'exchange': 'N/A'}
            )
            
            # Update metrics
            PredictionMetrics.objects.update_or_create(
                forecast_model=forecast_model,
                stock=stock,
                evaluation_date=datetime.now().date(),
                defaults={
                    'accuracy': metrics['accuracy'],
                    'precision': metrics.get('precision'),
                    'recall': metrics.get('recall'),
                    'f1_score': metrics.get('f1'),
                    'additional_metrics': {
                        'roc_auc': metrics.get('roc_auc'),
                        'execution_time': metrics['execution_time']
                    }
                }
            )
        
        logger.info("Model training and evaluation completed!")
        
        return summary_df

# Run the trainer if script is executed directly
if __name__ == "__main__":
    trainer = ModelTrainer()
    results = trainer.train_and_evaluate()