# backend/apps/predictions/ml_models/deep_learning.py

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input, Embedding, Bidirectional
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.metrics import AUC, Precision, Recall
from transformers import BertTokenizer, TFBertModel

class LSTMNewsModel:
    """
    LSTM deep learning model for market prediction from financial news
    """
    
    def __init__(self, max_words=10000, max_sequence_length=100, embedding_dim=100):
        self.max_words = max_words
        self.max_sequence_length = max_sequence_length
        self.embedding_dim = embedding_dim
        self.tokenizer = Tokenizer(num_words=self.max_words)
        self.model = None
        
    def preprocess_text(self, texts, train=False):
        """
        Preprocess texts and convert to sequences
        """
        if train:
            self.tokenizer.fit_on_texts(texts)
        
        sequences = self.tokenizer.texts_to_sequences(texts)
        padded_sequences = pad_sequences(sequences, maxlen=self.max_sequence_length)
        return padded_sequences
    
    def build_model(self):
        """
        Build LSTM model
        """
        model = Sequential()
        model.add(Embedding(input_dim=self.max_words, output_dim=self.embedding_dim, 
                           input_length=self.max_sequence_length))
        model.add(Bidirectional(LSTM(units=64, return_sequences=True)))
        model.add(Bidirectional(LSTM(units=32)))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(1, activation='sigmoid'))
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', AUC(), Precision(), Recall()]
        )
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, validation_data=None, epochs=10, batch_size=32):
        """
        Train the model
        """
        if self.model is None:
            self.build_model()
            
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
            ModelCheckpoint('best_lstm_model.h5', save_best_only=True)
        ]
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks
        )
        
        return history
    
    def predict(self, X_test):
        """
        Make predictions
        """
        predictions = self.model.predict(X_test)
        return (predictions > 0.5).astype(int).flatten()
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        """
        return self.model.evaluate(X_test, y_test)

class BERTNewsModel:
    """
    BERT-based deep learning model for market prediction from financial news
    """
    
    def __init__(self, max_length=128):
        self.max_length = max_length
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
    
    def build_model(self):
        """
        Build BERT-based model
        """
        input_ids = Input(shape=(self.max_length,), dtype=tf.int32, name='input_ids')
        attention_mask = Input(shape=(self.max_length,), dtype=tf.int32, name='attention_mask')
        
        bert_output = self.bert_model([input_ids, attention_mask])[0]
        cls_token = bert_output[:, 0, :]
        
        x = Dense(64, activation='relu')(cls_token)
        x = Dropout(0.2)(x)
        output = Dense(1, activation='sigmoid')(x)
        
        model = Model(inputs=[input_ids, attention_mask], outputs=output)
        
        # Freeze the BERT layers for fine-tuning
        for layer in model.layers[:2]:
            layer.trainable = False
        
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
        """
        if self.model is None:
            self.build_model()
            
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True),
            ModelCheckpoint('best_bert_model.h5', save_best_only=True)
        ]
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks
        )
        
        return history
    
    def predict(self, X_test):
        """
        Make predictions
        """
        predictions = self.model.predict(X_test)
        return (predictions > 0.5).astype(int).flatten()
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        """
        return self.model.evaluate(X_test, y_test)