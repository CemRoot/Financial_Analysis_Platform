# backend/apps/predictions/services/model_trainer.py

import logging
import os
import numpy as np
import pandas as pd
import pickle
import json
from datetime import datetime, timedelta
import tensorflow as tf
from django.conf import settings
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score

from ..data_processors.market_processor import MarketDataProcessor
from ..data_processors.news_processor import NewsProcessor
from ..data_processors.fetch_training_data import DataFetcher
from ..ml_models.traditional_models import MarketDirectionPredictor
from ..ml_models.deep_learning import LSTMNewsModel, BERTNewsModel
from ..ml_models.hybrid_models import HybridMarketNewsModel
from ..ml_models.model_evaluation import ModelEvaluator

logger = logging.getLogger(__name__)

class ModelTrainer:
    """
    ML modellerini eğiten servis sınıfı
    """
    
    def __init__(self):
        self.market_processor = MarketDataProcessor()
        self.news_processor = NewsProcessor()
        self.data_fetcher = DataFetcher()
        self.model_evaluator = ModelEvaluator()
        self.ml_models_dir = settings.ML_MODELS_DIR
        self.ml_temp_data_dir = settings.ML_TEMP_DATA_DIR
        
        # Dizinleri oluştur
        os.makedirs(self.ml_models_dir, exist_ok=True)
        os.makedirs(self.ml_temp_data_dir, exist_ok=True)
    
    def train_market_direction_model(self, model_type='logistic_regression', symbols=None, period='1y', test_size=0.2):
        """
        Piyasa yön tahmin modelini eğitir
        """
        try:
            # Sembolleri kontrol et, belirtilmemişse varsayılan bir liste kullan
            if not symbols:
                symbols = settings.DATA_COLLECTION['STOCK_SYMBOLS']
            
            # Eğitim verilerini topla
            logger.info(f"Fetching training data for {len(symbols)} symbols")
            all_features = []
            all_labels = []
            
            for symbol in symbols:
                # Her hisse senedi için geçmiş verileri al
                data = self.data_fetcher.fetch_historical_with_labels(symbol, period=period)
                
                if not data or 'features' not in data or 'labels' not in data:
                    logger.warning(f"No data fetched for {symbol}, skipping")
                    continue
                
                all_features.extend(data['features'])
                all_labels.extend(data['labels'])
            
            if not all_features or not all_labels:
                return {
                    "error": "No training data collected",
                    "status": "error"
                }
            
            # Eğitim ve test verilerini böl
            X_train, X_test, y_train, y_test = train_test_split(
                all_features, all_labels, test_size=test_size, random_state=42
            )
            
            # Modeli oluştur
            model = MarketDirectionPredictor(model_type=model_type)
            model.create_model()
            
            # Modeli eğit
            logger.info(f"Training {model_type} market direction model")
            model.train(X_train, y_train)
            
            # Modeli değerlendir
            eval_results = model.evaluate(X_test, y_test)
            
            # Hiperparametre optimizasyonu yap
            logger.info("Performing hyperparameter tuning")
            best_params = model.hyperparameter_tuning(X_train, y_train)
            
            # Optimizasyondan sonra son modeli eğit
            model.train(X_train, y_train)
            
            # Son modeli değerlendir
            final_eval = model.evaluate(X_test, y_test)
            
            # Modeli kaydet
            model_filename = f"{model_type}_direction_predictor.pkl"
            model_path = os.path.join(self.ml_models_dir, model_filename)
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Metrikleri kaydet
            metrics_filename = f"{model_type}_metrics.json"
            metrics_path = os.path.join(self.ml_models_dir, metrics_filename)
            
            metrics = {
                "accuracy": final_eval['accuracy'],
                "classification_report": final_eval['classification_report'],
                "best_params": best_params,
                "training_data": {
                    "symbols": symbols,
                    "period": period,
                    "samples": len(all_labels),
                    "features_count": len(all_features[0]) if all_features else 0,
                    "class_distribution": {
                        "up": all_labels.count(1),
                        "down": all_labels.count(0)
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            return {
                "model_type": model_type,
                "accuracy": final_eval['accuracy'],
                "model_path": model_path,
                "metrics_path": metrics_path,
                "best_params": best_params,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in train_market_direction_model: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def train_news_sentiment_model(self, model_type='lstm', test_size=0.2):
        """
        Haber duyarlılığı modeli eğitir
        """
        try:
            # Haber verilerini topla
            logger.info("Fetching news training data")
            news_data = self.data_fetcher.fetch_news_with_sentiment()
            
            if not news_data or 'texts' not in news_data or 'labels' not in news_data:
                return {
                    "error": "No news training data collected",
                    "status": "error"
                }
            
            texts = news_data['texts']
            labels = news_data['labels']
            
            # Verileri ön işle
            processed_texts = self.news_processor.preprocess_news_texts(texts)
            
            # Eğitim ve test verilerini böl
            X_train, X_test, y_train, y_test = train_test_split(
                processed_texts, labels, test_size=test_size, random_state=42
            )
            
            result = None
            
            # LSTM modeli
            if model_type == 'lstm':
                # Modeli oluştur
                lstm_model = LSTMNewsModel()
                
                # Tokenizer'ı eğit ve metinleri sayısal forma dönüştür
                X_train_processed = lstm_model.preprocess_text(X_train, train=True)
                X_test_processed = lstm_model.preprocess_text(X_test, train=False)
                
                # Modeli oluştur ve eğit
                model = lstm_model.build_model()
                history = lstm_model.train(
                    X_train_processed, 
                    np.array(y_train),
                    validation_data=(X_test_processed, np.array(y_test)),
                    epochs=5
                )
                
                # Modeli değerlendir
                y_pred = lstm_model.predict(X_test_processed)
                
                # Metrikleri hesapla
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                
                # Modeli kaydet
                model_path = os.path.join(self.ml_models_dir, 'lstm_news_model.h5')
                lstm_model.model.save_weights(model_path)
                
                # Tokenizer'ı kaydet
                tokenizer_path = os.path.join(self.ml_models_dir, 'lstm_tokenizer.pkl')
                with open(tokenizer_path, 'wb') as f:
                    pickle.dump(lstm_model.tokenizer, f)
                
                # Metrikleri kaydet
                metrics = {
                    "accuracy": float(accuracy),
                    "precision": float(precision),
                    "recall": float(recall),
                    "f1_score": float(f1),
                    "training_history": {
                        "loss": [float(loss) for loss in history.history['loss']],
                        "val_loss": [float(loss) for loss in history.history['val_loss']],
                        "accuracy": [float(acc) for acc in history.history['accuracy']],
                        "val_accuracy": [float(acc) for acc in history.history['val_accuracy']]
                    },
                    "training_data": {
                        "samples": len(labels),
                        "max_sequence_length": lstm_model.max_sequence_length,
                        "embedding_dim": lstm_model.embedding_dim,
                        "vocab_size": lstm_model.max_words,
                        "class_distribution": {
                            "positive": labels.count(1),
                            "negative": labels.count(0)
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                metrics_path = os.path.join(self.ml_models_dir, 'lstm_news_metrics.json')
                with open(metrics_path, 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                result = {
                    "model_type": "lstm",
                    "accuracy": float(accuracy),
                    "model_path": model_path,
                    "tokenizer_path": tokenizer_path,
                    "metrics_path": metrics_path,
                    "status": "success"
                }
                
            elif model_type == 'bert':
                # BERT modelini oluştur
                bert_model = BERTNewsModel()
                
                # Metinleri BERT formatına dönüştür
                X_train_processed = bert_model.preprocess_text(X_train)
                X_test_processed = bert_model.preprocess_text(X_test)
                
                # Modeli oluştur ve eğit
                model = bert_model.build_model()
                history = bert_model.train(
                    X_train_processed,
                    np.array(y_train),
                    validation_data=(X_test_processed, np.array(y_test)),
                    epochs=3  # BERT için daha az epoch yeterli
                )
                
                # Modeli değerlendir
                y_pred = bert_model.predict(X_test_processed)
                
                # Metrikleri hesapla
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                
                # Modeli kaydet
                model_path = os.path.join(self.ml_models_dir, 'bert_news_model.h5')
                bert_model.model.save_weights(model_path)
                
                # Metrikleri kaydet
                metrics = {
                    "accuracy": float(accuracy),
                    "precision": float(precision),
                    "recall": float(recall),
                    "f1_score": float(f1),
                    "training_history": {
                        "loss": [float(loss) for loss in history.history['loss']],
                        "val_loss": [float(loss) for loss in history.history['val_loss']],
                        "accuracy": [float(acc) for acc in history.history['accuracy']],
                        "val_accuracy": [float(acc) for acc in history.history['val_accuracy']]
                    },
                    "training_data": {
                        "samples": len(labels),
                        "max_length": bert_model.max_length,
                        "class_distribution": {
                            "positive": labels.count(1),
                            "negative": labels.count(0)
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                metrics_path = os.path.join(self.ml_models_dir, 'bert_news_metrics.json')
                with open(metrics_path, 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                result = {
                    "model_type": "bert",
                    "accuracy": float(accuracy),
                    "model_path": model_path,
                    "metrics_path": metrics_path,
                    "status": "success"
                }
            
            else:
                return {"error": f"Unsupported model type: {model_type}", "status": "error"}
            
            return result
            
        except Exception as e:
            logger.error(f"Error in train_news_sentiment_model: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def train_hybrid_model(self, symbols=None, test_size=0.2):
        """
        Piyasa verileri ve haberleri birleştiren hibrit bir model eğitir
        """
        try:
            # Sembolleri kontrol et, belirtilmemişse varsayılan bir liste kullan
            if not symbols:
                symbols = settings.DATA_COLLECTION['STOCK_SYMBOLS'][:5]  # Daha az sembol kullan
            
            logger.info(f"Fetching hybrid training data for {len(symbols)} symbols")
            
            # Veri toplayıcıları oluştur
            hybrid_data = self.data_fetcher.fetch_hybrid_training_data(symbols)
            
            if not hybrid_data or 'market_features' not in hybrid_data or 'news_features' not in hybrid_data:
                return {
                    "error": "No hybrid training data collected",
                    "status": "error"
                }
            
            # Eğitim verilerini böl
            X_market_train, X_market_test, X_news_train, X_news_test, y_train, y_test = train_test_split(
                hybrid_data['market_features'], 
                hybrid_data['news_features'], 
                hybrid_data['labels'],
                test_size=test_size, 
                random_state=42
            )
            
            # Hibrit model oluştur
            hybrid_model = HybridMarketNewsModel()
            model = hybrid_model.build_model(
                market_feature_dim=len(X_market_train[0]) if X_market_train else 0,
                news_feature_dim=len(X_news_train[0]) if X_news_train else 0
            )
            
            # Modeli eğit
            history = hybrid_model.train(
                [np.array(X_market_train), np.array(X_news_train)], 
                np.array(y_train),
                validation_data=([np.array(X_market_test), np.array(X_news_test)], np.array(y_test)),
                epochs=10
            )
            
            # Modeli değerlendir
            y_pred = hybrid_model.predict([np.array(X_market_test), np.array(X_news_test)])
            
            # Metrikleri hesapla
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            # Modeli kaydet
            model_path = os.path.join(self.ml_models_dir, 'hybrid_model.h5')
            hybrid_model.model.save_weights(model_path)
            
            # Veri işleme nesnelerini kaydet
            processing_path = os.path.join(self.ml_models_dir, 'hybrid_preprocessors.pkl')
            with open(processing_path, 'wb') as f:
                pickle.dump({
                    'market_scaler': hybrid_model.market_scaler,
                    'news_vectorizer': hybrid_model.news_vectorizer
                }, f)
            
            # Metrikleri kaydet
            metrics = {
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1),
                "training_history": {
                    "loss": [float(loss) for loss in history.history['loss']],
                    "val_loss": [float(loss) for loss in history.history['val_loss']],
                    "accuracy": [float(acc) for acc in history.history['accuracy']],
                    "val_accuracy": [float(acc) for acc in history.history['val_accuracy']]
                },
                "training_data": {
                    "symbols": symbols,
                    "samples": len(hybrid_data['labels']),
                    "market_features": len(X_market_train[0]) if X_market_train else 0,
                    "news_features": len(X_news_train[0]) if X_news_train else 0,
                    "class_distribution": {
                        "up": hybrid_data['labels'].count(1),
                        "down": hybrid_data['labels'].count(0)
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
            metrics_path = os.path.join(self.ml_models_dir, 'hybrid_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            return {
                "model_type": "hybrid",
                "accuracy": float(accuracy),
                "model_path": model_path,
                "processing_path": processing_path,
                "metrics_path": metrics_path,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in train_hybrid_model: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def train_all_models(self, symbols=None):
        """
        Tüm modelleri eğitir
        """
        try:
            results = {}
            
            # Geleneksel modelleri eğit
            logger.info("Training logistic regression model")
            lr_result = self.train_market_direction_model(model_type='logistic_regression', symbols=symbols)
            results['logistic_regression'] = lr_result
            
            logger.info("Training random forest model")
            rf_result = self.train_market_direction_model(model_type='random_forest', symbols=symbols)
            results['random_forest'] = rf_result
            
            # Derin öğrenme modellerini eğit
            logger.info("Training LSTM news model")
            lstm_result = self.train_news_sentiment_model(model_type='lstm')
            results['lstm'] = lstm_result
            
            # BERT modeli eğitimi opsiyonel olabilir (daha çok kaynak gerektirir)
            # logger.info("Training BERT news model")
            # bert_result = self.train_news_sentiment_model(model_type='bert')
            # results['bert'] = bert_result
            
            # Hibrit modeli eğit
            logger.info("Training hybrid model")
            hybrid_result = self.train_hybrid_model(symbols=symbols)
            results['hybrid'] = hybrid_result
            
            # Başarılı model sayısını hesapla
            success_count = sum(1 for model in results.values() if model.get('status') == 'success')
            
            return {
                "models_trained": len(results),
                "successful_models": success_count,
                "results": results,
                "status": "success" if success_count > 0 else "partial_success"
            }
            
        except Exception as e:
            logger.error(f"Error in train_all_models: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def evaluate_models(self, symbols=None, days=30):
        """
        Eğitilmiş modelleri geriye dönük test eder
        """
        try:
            if not symbols:
                symbols = settings.DATA_COLLECTION['STOCK_SYMBOLS'][:3]  # Az sayıda sembol kullan
            
            results = {}
            
            for symbol in symbols:
                # Test verilerini al
                test_data = self.data_fetcher.fetch_test_data(symbol, days=days)
                
                if not test_data or 'market_data' not in test_data or 'news_data' not in test_data:
                    logger.warning(f"No test data for {symbol}, skipping")
                    continue
                
                # Her model için test yap
                symbol_results = {}
                
                # Geleneksel modeller
                for model_type in ['logistic_regression', 'random_forest']:
                    model_path = os.path.join(self.ml_models_dir, f"{model_type}_direction_predictor.pkl")
                    
                    if not os.path.exists(model_path):
                        logger.warning(f"Model file not found: {model_path}")
                        continue
                    
                    # Modeli yükle
                    with open(model_path, 'rb') as f:
                        model = pickle.load(f)
                    
                    # Değerlendir
                    evaluation = self.model_evaluator.evaluate_direction_model(
                        model, test_data['market_data'], test_data['actual_directions']
                    )
                    
                    symbol_results[model_type] = evaluation
                
                # LSTM modeli
                lstm_model_path = os.path.join(self.ml_models_dir, 'lstm_news_model.h5')
                lstm_tokenizer_path = os.path.join(self.ml_models_dir, 'lstm_tokenizer.pkl')
                
                if os.path.exists(lstm_model_path) and os.path.exists(lstm_tokenizer_path):
                    # LSTM modelini yükle ve değerlendir
                    lstm_evaluation = self.model_evaluator.evaluate_news_model(
                        'lstm', test_data['news_data'], test_data['actual_directions']
                    )
                    
                    symbol_results['lstm'] = lstm_evaluation
                
                # Hibrit model
                hybrid_model_path = os.path.join(self.ml_models_dir, 'hybrid_model.h5')
                hybrid_processing_path = os.path.join(self.ml_models_dir, 'hybrid_preprocessors.pkl')
                
                if os.path.exists(hybrid_model_path) and os.path.exists(hybrid_processing_path):
                    # Hibrit modeli yükle ve değerlendir
                    hybrid_evaluation = self.model_evaluator.evaluate_hybrid_model(
                        test_data['market_data'], test_data['news_data'], test_data['actual_directions']
                    )
                    
                    symbol_results['hybrid'] = hybrid_evaluation
                
                results[symbol] = symbol_results
            
            # Tüm semboller için ortalama sonuçları hesapla
            averages = {}
            
            for model_type in ['logistic_regression', 'random_forest', 'lstm', 'hybrid']:
                model_results = [
                    symbol_results[model_type] 
                    for symbol_results in results.values() 
                    if model_type in symbol_results
                ]
                
                if model_results:
                    avg_accuracy = sum(r['accuracy'] for r in model_results) / len(model_results)
                    avg_precision = sum(r['precision'] for r in model_results) / len(model_results)
                    avg_recall = sum(r['recall'] for r in model_results) / len(model_results)
                    avg_f1 = sum(r['f1_score'] for r in model_results) / len(model_results)
                    
                    averages[model_type] = {
                        "accuracy": float(avg_accuracy),
                        "precision": float(avg_precision),
                        "recall": float(avg_recall),
                        "f1_score": float(avg_f1),
                        "symbols_tested": len(model_results)
                    }
            
            # Sonuçları kaydet
            evaluation_result = {
                "by_symbol": results,
                "averages": averages,
                "test_period": {
                    "days": days,
                    "end_date": datetime.now().strftime('%Y-%m-%d')
                },
                "symbols_tested": len(results),
                "timestamp": datetime.now().isoformat()
            }
            
            # Dosyaya kaydet
            eval_path = os.path.join(self.ml_models_dir, 'model_evaluation.json')
            with open(eval_path, 'w') as f:
                json.dump(evaluation_result, f, indent=2)
            
            return {
                "evaluation": evaluation_result,
                "evaluation_path": eval_path,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in evaluate_models: {str(e)}")
            return {"error": str(e), "status": "error"}
