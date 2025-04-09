# backend/apps/predictions/ml_models/traditional_models.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

class MarketDirectionPredictor:
    """
    Predicts market direction (up/down) using traditional machine learning models
    """
    
    def __init__(self, model_type="logistic_regression"):
        self.model_type = model_type
        self.model = None
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        
    def create_model(self):
        """
        Create appropriate model based on model_type
        """
        if self.model_type == "logistic_regression":
            self.model = Pipeline([
                ('tfidf', self.vectorizer),
                ('classifier', LogisticRegression(max_iter=1000, class_weight='balanced'))
            ])
        elif self.model_type == "random_forest":
            self.model = Pipeline([
                ('tfidf', self.vectorizer),
                ('classifier', RandomForestClassifier(n_estimators=100, class_weight='balanced'))
            ])
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        return self.model
    
    def hyperparameter_tuning(self, X_train, y_train, cv=5):
        """
        Perform hyperparameter tuning using grid search
        """
        if self.model_type == "logistic_regression":
            param_grid = {
                'classifier__C': [0.01, 0.1, 1, 10],
                'classifier__penalty': ['l1', 'l2'],
                'classifier__solver': ['liblinear', 'saga']
            }
        elif self.model_type == "random_forest":
            param_grid = {
                'classifier__n_estimators': [50, 100, 200],
                'classifier__max_depth': [None, 10, 20, 30],
                'classifier__min_samples_split': [2, 5, 10]
            }
        
        grid_search = GridSearchCV(self.model, param_grid, cv=cv, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X_train, y_train)
        
        self.model = grid_search.best_estimator_
        return grid_search.best_params_
    
    def train(self, X_train, y_train):
        """
        Train the model
        """
        if self.model is None:
            self.create_model()
        self.model.fit(X_train, y_train)
        return self
    
    def predict(self, X_test):
        """
        Make predictions
        """
        return self.model.predict(X_test)
    
    def predict_proba(self, X_test):
        """
        Get probability estimates
        """
        return self.model.predict_proba(X_test)
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        """
        y_pred = self.predict(X_test)
        
        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        return results