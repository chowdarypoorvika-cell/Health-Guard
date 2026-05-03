from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd
import joblib
import os

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        self.is_trained = False

    def train(self, data):
        """
        data: list of dicts or pandas DataFrame with features [heart_rate, temperature, spo2]
        """
        try:
            df = pd.DataFrame(data)
            # Use more features if available
            feature_cols = ['heart_rate', 'temperature', 'spo2']
            available_cols = [col for col in feature_cols if col in df.columns]
            
            if len(available_cols) < 2:
                raise ValueError("Need at least 2 features for training")
            
            features = df[available_cols]
            self.model.fit(features)
            self.is_trained = True
            print("Anomaly Detector trained successfully.")
        except Exception as e:
            print(f"Training error: {e}")
            self.is_trained = False
            raise

    def predict(self, data_point):
        """
        data_point: dict with keys [heart_rate, temperature, spo2]
        returns: True for anomaly, False for normal
        """
        if not self.is_trained:
            return False # Fallback to normal if not trained
        
        try:
            df = pd.DataFrame([data_point])
            # Use same features as training
            feature_cols = ['heart_rate', 'temperature', 'spo2']
            available_cols = [col for col in feature_cols if col in df.columns]
            
            if len(available_cols) < 2:
                return False
            
            features = df[available_cols]
            prediction = self.model.predict(features)[0]
            # Isolation Forest: -1 anomaly, 1 normal
            # We'll return True if anomaly (-1), False if normal (1)
            return prediction == -1
        except Exception as e:
            print(f"Prediction error: {e}")
            return False  # Safe fallback

if __name__ == "__main__":
    # Test
    from simulation import VitalSignGenerator
    gen = VitalSignGenerator()
    training_data = [gen.generate_packet() for _ in range(200)]
    
    detector = AnomalyDetector()
    detector.train(training_data)
    
    normal_point = gen.generate_packet()
    anomaly_point = gen.generate_packet(anomaly_type='spike')
    
    print(f"Normal point prediction (Is Anomaly?): {detector.predict(normal_point)}")
    print(f"Anomaly point prediction (Is Anomaly?): {detector.predict(anomaly_point)}")
