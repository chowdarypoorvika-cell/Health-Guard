import random
import numpy as np
import time
from datetime import datetime

class VitalSignGenerator:
    def __init__(self):
        # Base values for normal vitals
        self.base_hr = 75
        self.base_temp = 37.0
        self.base_spo2 = 98.0
        self.base_bp_sys = 120
        self.base_bp_dia = 80
        self.base_resp_rate = 16
        
        # Attack trigger state
        self.active_attack = None
        self.attack_duration = 0
        
        # Statistics tracking
        self.total_packets = 0
        self.anomaly_count = 0
        self.attack_history = []
        
        # Patient profiles for multi-patient simulation
        self.patients = {
            "P001": {"name": "John Doe", "age": 45, "condition": "Cardiac Monitoring", "hr_base": 72, "risk": "medium"},
            "P002": {"name": "Jane Smith", "age": 32, "condition": "Post-Surgery", "hr_base": 78, "risk": "low"},
            "P003": {"name": "Robert Chen", "age": 67, "condition": "ICU Critical", "hr_base": 85, "risk": "high"},
        }
        self.current_patient = "P001"

    def set_patient(self, patient_id):
        """Switch to a different patient profile"""
        if patient_id in self.patients:
            self.current_patient = patient_id
            patient = self.patients[patient_id]
            self.base_hr = patient["hr_base"]
            return True
        return False

    def get_patients(self):
        """Return all patient profiles"""
        return self.patients

    def get_current_patient(self):
        """Return current patient info"""
        return {
            "id": self.current_patient,
            **self.patients[self.current_patient]
        }

    def set_attack(self, attack_type, duration=10):
        """Manually trigger an attack for 'duration' packets"""
        self.active_attack = attack_type
        self.attack_duration = duration
        self.attack_history.append({
            "type": attack_type,
            "timestamp": datetime.now().isoformat(),
            "duration": duration
        })
        
    def get_statistics(self):
        """Return current statistics"""
        return {
            "total_packets": self.total_packets,
            "anomaly_count": self.anomaly_count,
            "anomaly_rate": round((self.anomaly_count / max(1, self.total_packets)) * 100, 2),
            "recent_attacks": self.attack_history[-10:],  # Last 10 attacks
            "current_patient": self.get_current_patient()
        }
    
    def clear_attack(self):
        """Clear any active attack"""
        self.active_attack = None
        self.attack_duration = 0
        
    def generate_packet(self, anomaly_type=None):
        """
        Generates a single data packet.
        anomaly_type: override, used for internal logic (random injection)
        """
        timestamp = time.time()
        self.total_packets += 1
        
        # Check for manual attack override
        if self.attack_duration > 0 and self.active_attack:
            anomaly_type = self.active_attack
            self.attack_duration -= 1
        elif self.attack_duration <= 0:
            self.active_attack = None
        
        # Normal fluctuations based on current patient
        patient = self.patients[self.current_patient]
        hr = int(np.random.normal(patient["hr_base"], 5))
        temp = round(np.random.normal(self.base_temp, 0.2), 1)
        spo2 = int(np.clip(np.random.normal(self.base_spo2, 1), 90, 100))
        bp_sys = int(np.random.normal(self.base_bp_sys, 8))
        bp_dia = int(np.random.normal(self.base_bp_dia, 5))
        resp_rate = int(np.random.normal(self.base_resp_rate, 2))
        
        is_anomaly = 0
        severity = "normal"
        threat_details = ""
        
        if anomaly_type:
            is_anomaly = 1
            self.anomaly_count += 1
            
            if anomaly_type == 'spike':
                # Simulate a sudden spike (e.g., sensor error or attack)
                hr += random.randint(40, 80)
                temp += random.uniform(2.0, 5.0)
                bp_sys += random.randint(30, 60)
                severity = "high"
                threat_details = "Abnormal vital spike detected - possible sensor manipulation"
                
            elif anomaly_type == 'flatline':
                # Sensor disconnected or death (often zero or static)
                hr = 0
                temp = 0.0
                spo2 = 0
                bp_sys = 0
                bp_dia = 0
                resp_rate = 0
                severity = "critical"
                threat_details = "Complete signal loss - DoS attack or sensor failure"
                
            elif anomaly_type == 'spoof':
                # Subtle spoofing - values that look normal but are rigidly calculated
                hr = 60  # Fixed value
                temp = 36.5  # Fixed value
                spo2 = 99
                bp_sys = 120
                bp_dia = 80
                severity = "medium"
                threat_details = "Suspiciously stable readings - possible data spoofing"
                
            elif anomaly_type == 'noise':
                # Random high variance noise
                hr = random.randint(30, 180)
                temp = round(random.uniform(34.0, 42.0), 1)
                spo2 = random.randint(60, 100)
                bp_sys = random.randint(70, 200)
                bp_dia = random.randint(40, 120)
                resp_rate = random.randint(5, 40)
                severity = "high"
                threat_details = "High variance noise injection - data integrity compromised"
                
            elif anomaly_type == 'replay':
                # Replay attack - same values repeated
                hr = 75
                temp = 37.0
                spo2 = 98
                bp_sys = 120
                bp_dia = 80
                severity = "medium"
                threat_details = "Repeated identical values - possible replay attack"
                
            elif anomaly_type == 'mitm':
                # Man-in-the-middle - slightly altered values
                hr = int(patient["hr_base"] * 0.85)
                temp = round(self.base_temp - 0.5, 1)
                spo2 = 94
                severity = "high"
                threat_details = "Subtly altered values detected - possible MITM attack"
                
        return {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "patient_id": self.current_patient,
            "patient_name": patient["name"],
            "heart_rate": hr,
            "temperature": temp,
            "spo2": spo2,
            "blood_pressure": f"{bp_sys}/{bp_dia}",
            "bp_systolic": bp_sys,
            "bp_diastolic": bp_dia,
            "respiratory_rate": resp_rate,
            "is_anomaly_injected": bool(is_anomaly),
            "attack_type": anomaly_type if is_anomaly else "Normal",
            "severity": severity,
            "threat_details": threat_details,
            "risk_level": patient["risk"]
        }


class ThreatIntelligence:
    """Tracks and analyzes threat patterns"""
    
    def __init__(self):
        self.threats = []
        self.threat_counts = {
            "spike": 0,
            "flatline": 0,
            "spoof": 0,
            "noise": 0,
            "replay": 0,
            "mitm": 0
        }
        self.blocked_count = 0
        self.detected_count = 0
        
    def log_threat(self, threat_type, detected=True, blocked=False):
        """Log a threat event"""
        self.threats.append({
            "type": threat_type,
            "timestamp": datetime.now().isoformat(),
            "detected": detected,
            "blocked": blocked
        })
        if threat_type in self.threat_counts:
            self.threat_counts[threat_type] += 1
        if detected:
            self.detected_count += 1
        if blocked:
            self.blocked_count += 1
            
    def get_summary(self):
        """Get threat intelligence summary"""
        return {
            "total_threats": len(self.threats),
            "detected": self.detected_count,
            "blocked": self.blocked_count,
            "by_type": self.threat_counts,
            "recent": self.threats[-20:],
            "detection_rate": round((self.detected_count / max(1, len(self.threats))) * 100, 1)
        }


if __name__ == "__main__":
    gen = VitalSignGenerator()
    for _ in range(5):
        print(gen.generate_packet())
        print(gen.generate_packet(anomaly_type='spike'))
