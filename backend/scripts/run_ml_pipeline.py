# backend/scripts/run_ml_pipeline.py

import os
import sys
import logging
import argparse
import schedule
import time
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ml_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_data_collection():
    """Run the data collection process"""
    logger.info("Starting data collection...")
    
    try:
        # Import within function to ensure Django is properly configured
        from scripts.data_collection.fetch_training_data import TrainingDataCollector
        
        collector = TrainingDataCollector(days_back=90)
        training_data = collector.create_training_dataset()
        
        if training_data is not None:
            logger.info("Data collection completed successfully")
            return True
        else:
            logger.error("Data collection failed")
            return False
    
    except Exception as e:
        logger.error(f"Error in data collection: {str(e)}")
        return False

def run_model_training():
    """Run the model training process"""
    logger.info("Starting model training...")
    
    try:
        # Import within function to ensure Django is properly configured
        from scripts.ml_scripts.train_models import ModelTrainer
        
        trainer = ModelTrainer()
        results = trainer.train_and_evaluate()
        
        if results is not None:
            logger.info("Model training completed successfully")
            return True
        else:
            logger.error("Model training failed")
            return False
    
    except Exception as e:
        logger.error(f"Error in model training: {str(e)}")
        return False

def run_full_pipeline():
    """Run the full ML pipeline"""
    logger.info("Running full ML pipeline...")
    
    # Run data collection
    if run_data_collection():
        # If data collection succeeds, run model training
        run_model_training()
    
    logger.info("ML pipeline completed")

def schedule_pipeline(interval_days=7):
    """Schedule the pipeline to run periodically"""
    logger.info(f"Scheduling ML pipeline to run every {interval_days} days")
    
    # Set the schedule
    schedule.every(interval_days).days.at("02:00").do(run_full_pipeline)
    
    logger.info(f"Next run scheduled for: {schedule.next_run()}")
    
    # Run immediately once
    run_full_pipeline()
    
    # Keep the script running and execute scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the ML pipeline')
    parser.add_argument('--collect-data', action='store_true', help='Run data collection')
    parser.add_argument('--train-models', action='store_true', help='Run model training')
    parser.add_argument('--full-pipeline', action='store_true', help='Run the full pipeline')
    parser.add_argument('--schedule', type=int, help='Schedule the pipeline to run every N days')
    
    args = parser.parse_args()
    
    if args.collect_data:
        run_data_collection()
    elif args.train_models:
        run_model_training()
    elif args.full_pipeline:
        run_full_pipeline()
    elif args.schedule:
        schedule_pipeline(args.schedule)
    else:
        # If no arguments, run the full pipeline once
        run_full_pipeline()