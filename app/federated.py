import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from simulation import VitalSignGenerator

class FederatedSimulator:
    def __init__(self):
        self.gen = VitalSignGenerator()
        
    def generate_dataset(self, size=500):
        data = []
        labels = [] # 0: Normal, 1: Anomaly
        
        # Force at least one anomaly and one normal to ensure classes
        # Normal
        packet = self.gen.generate_packet()
        labels.append(0)
        data.append([packet['heart_rate'], packet['temperature'], packet['spo2']])
        
        # Anomaly
        packet = self.gen.generate_packet(anomaly_type='spike')
        labels.append(1)
        data.append([packet['heart_rate'], packet['temperature'], packet['spo2']])
        
        attack_types = ['spike', 'flatline', 'spoof', 'noise', 'replay', 'mitm']
        for _ in range(size - 2):
            # Mix of normal and anomaly
            if np.random.rand() > 0.8: # 20% anomalies
                attack_type = np.random.choice(attack_types)
                packet = self.gen.generate_packet(anomaly_type=attack_type)
                labels.append(1)
            else:
                packet = self.gen.generate_packet()
                labels.append(0)
            data.append([packet['heart_rate'], packet['temperature'], packet['spo2']])
            
        return np.array(data), np.array(labels)

    def run_simulation(self, rounds=5):
        # 1. Simulate datasets for Hospital A and Hospital B
        X_a, y_a = self.generate_dataset(size=200)
        X_b, y_b = self.generate_dataset(size=200)
        
        # Test set for global model
        X_test, y_test = self.generate_dataset(size=100)

        # Initialize models
        model_a = LogisticRegression(max_iter=10, warm_start=True) # Partial fit simulation
        model_b = LogisticRegression(max_iter=10, warm_start=True)
        global_model = LogisticRegression(max_iter=10, warm_start=True)
        
        # Initialize global model
        global_model.fit(X_a, y_a)
        
        history = []
        
        for r in range(1, rounds + 1):
            # Simulate local training steps (incremental learning)
            # In a real scenario, this would be new data or more epochs.
            # Here we just refit on the same data to simulate "work"
            model_a.fit(X_a, y_a)
            model_b.fit(X_b, y_b)
            
            # Simulated Aggregation
            # We mix the global weights back into local to simulate the cycle 
            # (Simplification for simulation: just averaging local to get global)
            global_coef = (model_a.coef_ + model_b.coef_) / 2
            global_intercept = (model_a.intercept_ + model_b.intercept_) / 2
            
            global_model.coef_ = global_coef
            global_model.intercept_ = global_intercept
            
            # Evaluate
            acc_a = accuracy_score(y_test, model_a.predict(X_test))
            acc_b = accuracy_score(y_test, model_b.predict(X_test))
            acc_global = accuracy_score(y_test, global_model.predict(X_test))
            
            history.append({
                "round": r,
                "hospital_a_accuracy": round(acc_a, 4),
                "hospital_b_accuracy": round(acc_b, 4),
                "global_model_accuracy": round(acc_global, 4)
            })
        
        return {
            "history": history,
            "final_accuracy": round(acc_global, 4),
            "message": f"Federated Learning complete after {rounds} rounds."
        }

if __name__ == "__main__":
    fed = FederatedSimulator()
    print(fed.run_simulation())
