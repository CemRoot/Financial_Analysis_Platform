# backend/apps/predictions/ml_models/model_evaluation.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve
)
import time

class ModelEvaluator:
    """
    Class for evaluating and comparing multiple machine learning models
    """
    
    def __init__(self):
        self.models = {}
        self.predictions = {}
        self.scores = {}
        self.execution_times = {}
        
    def add_model(self, name, model):
        """
        Add a model for evaluation
        """
        self.models[name] = model
        return self
    
    def evaluate_all(self, X_test, y_test):
        """
        Evaluate all models
        """
        for name, model in self.models.items():
            # Measure execution time
            start_time = time.time()
            y_pred = model.predict(X_test)
            end_time = time.time()
            
            self.predictions[name] = y_pred
            self.execution_times[name] = end_time - start_time
            
            # Calculate performance metrics
            self.scores[name] = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1': f1_score(y_test, y_pred),
                'execution_time': self.execution_times[name]
            }
            
            # Add AUC-ROC if model supports probability prediction
            if hasattr(model, 'predict_proba'):
                y_prob = model.predict_proba(X_test)[:, 1]
                self.scores[name]['roc_auc'] = roc_auc_score(y_test, y_prob)
        
        return self.scores
    
    def get_summary_dataframe(self):
        """
        Return a DataFrame with comparison results
        """
        if not self.scores:
            raise ValueError("Evaluate models first using evaluate_all method")
        
        # Create DataFrame for model comparison
        summary = pd.DataFrame(self.scores).T
        summary = summary.sort_values('f1', ascending=False)
        
        return summary
    
    def plot_confusion_matrices(self, y_test, figsize=(15, 5)):
        """
        Plot confusion matrices for all models
        """
        if not self.predictions:
            raise ValueError("Evaluate models first using evaluate_all method")
        
        n_models = len(self.predictions)
        fig, axes = plt.subplots(1, n_models, figsize=figsize)
        
        if n_models == 1:
            axes = [axes]
        
        for i, (name, y_pred) in enumerate(self.predictions.items()):
            cm = confusion_matrix(y_test, y_pred)
            sns.heatmap(cm, annot=True, fmt='d', ax=axes[i], cmap='Blues')
            axes[i].set_title(f'Confusion Matrix - {name}')
            axes[i].set_xlabel('Predicted')
            axes[i].set_ylabel('Actual')
        
        plt.tight_layout()
        return fig
    
    def plot_roc_curves(self, X_test, y_test, figsize=(10, 6)):
        """
        Plot ROC curves for models that support predict_proba
        """
        plt.figure(figsize=figsize)
        
        for name, model in self.models.items():
            if hasattr(model, 'predict_proba'):
                y_prob = model.predict_proba(X_test)[:, 1]
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                plt.plot(fpr, tpr, label=f'{name} (AUC = {self.scores[name]["roc_auc"]:.3f})')
        
        plt.plot([0, 1], [0, 1], 'k--')  # Random prediction line
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves')
        plt.legend()
        
        return plt.gcf()
    
    def plot_execution_times(self, figsize=(10, 6)):
        """
        Plot execution times for all models
        """
        plt.figure(figsize=figsize)
        
        # Plot execution times
        plt.bar(self.execution_times.keys(), self.execution_times.values())
        plt.title('Model Execution Times')
        plt.xlabel('Model')
        plt.ylabel('Time (seconds)')
        plt.xticks(rotation=45)
        
        return plt.gcf()