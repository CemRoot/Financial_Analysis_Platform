# backend/apps/predictions/ml_models/hybrid_models.py

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input, Concatenate
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.metrics import AUC, Precision, Recall
from transformers import BertTokenizer, TFBertModel

class HybridMarketNewsModel:
    """
    Hybrid model combining market data and news data for financial market prediction
    """
    
    def __init__(self, max_length=128, lstm_units=32):
        self.max_length = max_length
        self.lstm_units = lstm_units
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = TFBertModel.from_pretrained('bert-base-uncased')
        self.model = None
        
    def preprocess_text(self, texts):
        """
        Preprocess texts with BERT tokenizer
        """
        encoded_inputs = self.tokenizer(
            texts,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='tf'
        )
        
        return {'input_ids': encoded_inputs['input_ids'], 
                'attention_mask': encoded_inputs['attention_mask']}
    
    def build_model(self, market_feature_dim=12):
        """
        Build hybrid model combining market data and news data
        
        Args:
            market_feature_dim: Dimension of market features vector
        """
        # BERT inputs for news data
        input_ids = Input(shape=(self.max_length,), dtype=tf.int32, name='input_ids')
        attention_mask = Input(shape=(self.max_length,), dtype=tf.int32, name='attention_mask')
        
        # Market data input
        market_input = Input(shape=(market_feature_dim,), dtype=tf.float32, name='market_features')
        
        # Process news data with BERT
        bert_output = self.bert_model([input_ids, attention_mask])[0]  # Sequence output
        
        # LSTM layer for news
        lstm_output = LSTM(self.lstm_units, return_sequences=False)(bert_output)
        
        # CLS token (first token)
        cls_token = bert_output[:, 0, :]
        
        # Combine BERT and LSTM outputs for news
        news_features = Concatenate()([cls_token, lstm_output])
        news_features = Dense(64, activation='relu')(news_features)
        news_features = Dropout(0.2)(news_features)
        
        # Process market data
        market_features = Dense(32, activation='relu')(market_input)
        market_features = Dropout(0.1)(market_features)
        
        # Combine news and market features
        combined_features = Concatenate()([news_features, market_features])
        
        # Final classification layers
        x = Dense(64, activation='relu')(combined_features)
        x = Dropout(0.2)(x)
        output = Dense(1, activation='sigmoid')(x)
        
        # Create model
        model = Model(inputs=[input_ids, attention_mask, market_input], outputs=output)
        
        # Freeze BERT layers
        self.bert_model.trainable = False
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', AUC(), Precision(), Recall()]
        )
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, validation_data=None, epochs=5, batch_size=16):
        """
        Train the model
        
        Args:
            X_train: Dict with 'news' (input_ids, attention_mask) and 'market' (features)
            y_train: Target labels
            validation_data: Validation data in same format as X_train, y_train
            epochs: Number of training epochs
            batch_size: Batch size
        """
        if self.model is None:
            raise ValueError("Model must be built before training")
            
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True),
            ModelCheckpoint('best_hybrid_model.h5', save_best_only=True)
        ]
        
        # Prepare inputs
        train_inputs = [
            X_train['news']['input_ids'], 
            X_train['news']['attention_mask'],
            X_train['market']
        ]
        
        val_inputs = None
        if validation_data:
            val_inputs = [
                validation_data[0]['news']['input_ids'],
                validation_data[0]['news']['attention_mask'],
                validation_data[0]['market']
            ]
            val_targets = validation_data[1]
            validation_data = (val_inputs, val_targets)
        
        history = self.model.fit(
            train_inputs, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks
        )
        
        return history
    
    def predict(self, X_test):
        """
        Make predictions
        
        Args:
            X_test: Dict with 'news' (input_ids, attention_mask) and 'market' (features)
        """
        # Prepare inputs
        test_inputs = [
            X_test['news']['input_ids'], 
            X_test['news']['attention_mask'],
            X_test['market']
        ]
        
        predictions = self.model.predict(test_inputs)
        return (predictions > 0.5).astype(int).flatten()
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        """
        # Prepare inputs
        test_inputs = [
            X_test['news']['input_ids'], 
            X_test['news']['attention_mask'],
            X_test['market']
        ]
        
        return self.model.evaluate(test_inputs, y_test)