"""
Train a custom ML model for CloudGuard AI
Model learns to predict security risk levels and recommendations
This script runs locally OR on SageMaker
"""

import pandas as pd
import numpy as np
import json
import os
import sys
import pickle
from datetime import datetime, timezone

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error, r2_score, accuracy_score
import joblib

# Logging
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SecurityRiskModel:
    """ML Model for predicting security risk and recommendations"""
    
    def __init__(self):
        self.severity_classifier = None
        self.risk_score_predictor = None
        self.cost_predictor = None
        self.label_encoders = {}
        self.feature_columns = None
        self.feature_scaler = None
        
    def load_and_prepare_data(self, data_path):
        """Load CSV and prepare for training"""
        logger.info(f"📊 Loading data from {data_path}")
        
        df = pd.read_csv(data_path)
        logger.info(f"✅ Loaded {len(df)} training examples")
        logger.info(f"Columns: {list(df.columns)}")
        
        return df
    
    def preprocess_data(self, df):
        """Convert data to ML-ready format"""
        logger.info("🔄 Preprocessing data...")
        
        # Handle missing values
        df = df.fillna(0)
        
        # Encode categorical variables
        categorical_cols = ['finding_type', 'resource_type', 'severity']
        
        for col in categorical_cols:
            if col in df.columns:
                encoder = LabelEncoder()
                df[col + '_encoded'] = encoder.fit_transform(df[col])
                self.label_encoders[col] = encoder
                logger.info(f"  Encoded {col}: {list(encoder.classes_)}")
        
        # Select features for model
        self.feature_columns = [
            'is_public',
            'is_encrypted',
            'port_exposed',
            'finding_type_encoded',
            'resource_type_encoded',
            'severity_encoded'
        ]
        
        # Create feature matrix and targets
        X = df[self.feature_columns].values.astype(float)
        y_impact = df['business_impact_score'].values
        y_severity = df['severity'].values
        y_cost = df['estimated_breach_cost'].values
        
        logger.info(f"✅ Features prepared: {len(X)} samples, {len(self.feature_columns)} features")
        logger.info(f"Features: {self.feature_columns}")
        
        return X, y_severity, y_impact, y_cost, df
    
    def train_models(self, X, y_severity, y_impact, y_cost):
        """Train multiple models"""
        logger.info("\n" + "="*60)
        logger.info("🤖 Training models...")
        logger.info("="*60 + "\n")
        
        # Split data (80-20 split)
        X_train, X_test, y_sev_train, y_sev_test, y_imp_train, y_imp_test, y_cost_train, y_cost_test = train_test_split(
            X, y_severity, y_impact, y_cost,
            test_size=0.2,
            random_state=42
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples\n")
        
        # Model 1: Severity Classifier
        logger.info("1️⃣ Training Severity Classifier (Random Forest)...")
        self.severity_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.severity_classifier.fit(X_train, y_sev_train)
        
        sev_pred = self.severity_classifier.predict(X_test)
        sev_accuracy = accuracy_score(y_sev_test, sev_pred)
        logger.info(f"   ✅ Accuracy: {sev_accuracy:.2%}\n")
        
        # Model 2: Risk Score Predictor
        logger.info("2️⃣ Training Risk Score Predictor (Gradient Boosting)...")
        self.risk_score_predictor = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.risk_score_predictor.fit(X_train, y_imp_train)
        
        risk_r2 = r2_score(y_imp_test, self.risk_score_predictor.predict(X_test))
        logger.info(f"   ✅ R² Score: {risk_r2:.2%}\n")
        
        # Model 3: Breach Cost Predictor
        logger.info("3️⃣ Training Cost Predictor (Gradient Boosting)...")
        self.cost_predictor = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.cost_predictor.fit(X_train, y_cost_train)
        
        cost_r2 = r2_score(y_cost_test, self.cost_predictor.predict(X_test))
        logger.info(f"   ✅ R² Score: {cost_r2:.2%}\n")
        
        logger.info("="*60)
        logger.info("✅ All models trained successfully!")
        logger.info("="*60 + "\n")
    
    def save_models(self, model_dir):
        """Save trained models to disk"""
        logger.info(f"💾 Saving models to {model_dir}")
        
        os.makedirs(model_dir, exist_ok=True)
        
        # Save models
        joblib.dump(self.severity_classifier, os.path.join(model_dir, 'severity_model.pkl'))
        joblib.dump(self.risk_score_predictor, os.path.join(model_dir, 'risk_model.pkl'))
        joblib.dump(self.cost_predictor, os.path.join(model_dir, 'cost_model.pkl'))
        joblib.dump(self.label_encoders, os.path.join(model_dir, 'encoders.pkl'))
        
        # Save metadata
        metadata = {
            'feature_columns': self.feature_columns,
            'label_encoders': {k: list(v.classes_) for k, v in self.label_encoders.items()},
            'trained_at': datetime.now(timezone.utc).isoformat(),
            'model_version': '1.0',
            'model_components': {
                'severity_classifier': 'RandomForestClassifier (100 trees)',
                'risk_score_predictor': 'GradientBoostingRegressor',
                'cost_predictor': 'GradientBoostingRegressor'
            }
        }
        
        with open(os.path.join(model_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Models saved to:")
        logger.info(f"   - {os.path.join(model_dir, 'severity_model.pkl')}")
        logger.info(f"   - {os.path.join(model_dir, 'risk_model.pkl')}")
        logger.info(f"   - {os.path.join(model_dir, 'cost_model.pkl')}")
        logger.info(f"   - {os.path.join(model_dir, 'encoders.pkl')}")
        logger.info(f"   - {os.path.join(model_dir, 'metadata.json')}\n")


def main():
    """Main training pipeline"""
    logger.info("\n" + "="*60)
    logger.info("🚀 CloudGuard Security ML Model Training Started")
    logger.info("="*60 + "\n")
    
    # Get paths from arguments or use defaults
    data_path = sys.argv[1] if len(sys.argv) > 1 else 'security_training_data.csv'
    model_output_path = sys.argv[2] if len(sys.argv) > 2 else './output'
    
    logger.info(f"📥 Input:  {os.path.abspath(data_path)}")
    logger.info(f"📤 Output: {os.path.abspath(model_output_path)}\n")
    
    # Create and train model
    model = SecurityRiskModel()
    
    # Load data
    df = model.load_and_prepare_data(data_path)
    
    # Prepare
    X, y_severity, y_impact, y_cost, df_processed = model.preprocess_data(df)
    
    # Train
    model.train_models(X, y_severity, y_impact, y_cost)
    
    # Save
    model.save_models(model_output_path)
    
    logger.info("="*60)
    logger.info("✅ TRAINING COMPLETE - READY FOR DEPLOYMENT!")
    logger.info("="*60 + "\n")


if __name__ == '__main__':
    main()